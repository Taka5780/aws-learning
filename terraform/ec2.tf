# Security Group (Firewall)
resource "aws_security_group" "allow_ssh_and_http" {
  name        = "allow_ssh"
  description = "Allow SSH and HTTP inbound traffic"
  vpc_id      = aws_vpc.dev_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
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

# EC2 instance
resource "aws_instance" "web" {
  ami           = "ami-088b486f20fab3f0e"
  instance_type = var.instance_type

  key_name               = var.key_name
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.allow_ssh_and_http.id]

  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name
  tags = {
    Name = "terraform-study-ec2"
  }
}
