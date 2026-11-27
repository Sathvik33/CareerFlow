terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

provider "aws" {
  region = "ap-south-1" # Change if you use a different AWS region
}

# 1. Auto-generate SSH key pair (no manual key_name needed)
resource "tls_private_key" "careerflow_ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "careerflow_key" {
  key_name   = "careerflow-auto-key"
  public_key = tls_private_key.careerflow_ssh.public_key_openssh
}

resource "local_sensitive_file" "private_key_pem" {
  filename        = "${path.module}/careerflow-auto-key.pem"
  content         = tls_private_key.careerflow_ssh.private_key_pem
  file_permission = "0400"
}

# 2. Fetch latest Ubuntu 24.04 LTS AMI (099720109477 is Canonical's public ID)
data "aws_ami" "ubuntu" {
  most_recent = true    
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

# 3. Security Group
resource "aws_security_group" "careerflow_sg" {
  name        = "careerflow-tf-sg"
  description = "Allow SSH, HTTP, and HTTPS for CareerFlow"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 4. EC2 Instance
resource "aws_instance" "careerflow_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro" # Change to "m7i-flex.large" if you prefer more RAM
  key_name               = aws_key_pair.careerflow_key.key_name
  vpc_security_group_ids = [aws_security_group.careerflow_sg.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name = "CareerFlow-Server"
  }
}

# 5. Auto-generate Ansible inventory with the new IP and auto-created key
resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../ansible/inventory.ini"
  content  = <<-EOT
    [app_server]
    careerflow ansible_host=${aws_instance.careerflow_server.public_ip} ansible_user=ubuntu ansible_ssh_private_key_file=${abspath(local_sensitive_file.private_key_pem.filename)} ansible_ssh_common_args='-o StrictHostKeyChecking=no'
  EOT
}

output "careerflow_public_ip" {
  value = aws_instance.careerflow_server.public_ip
}