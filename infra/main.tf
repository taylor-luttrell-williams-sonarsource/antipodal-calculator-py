# SonarQube demo fixture: this Terraform intentionally provisions insecure
# infrastructure so the IaC analyzer has something to report.

provider "aws" {
  region = "us-east-1"

  # SECURITY: hardcoded provider credentials committed to source control.
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

# SECURITY: publicly readable bucket, no encryption, no versioning, no logging.
resource "aws_s3_bucket" "antipode_exports" {
  bucket = "antipodal-calculator-exports"
  acl    = "public-read"
}

resource "aws_s3_bucket_public_access_block" "antipode_exports" {
  bucket                  = aws_s3_bucket.antipode_exports.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# SECURITY: bucket policy grants read access to every principal.
resource "aws_s3_bucket_policy" "antipode_exports" {
  bucket = aws_s3_bucket.antipode_exports.id

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::antipodal-calculator-exports/*"
    }
  ]
}
POLICY
}

# SECURITY: security group open to the entire internet on admin ports.
resource "aws_security_group" "antipode_api" {
  name        = "antipode-api"
  description = "Antipodal calculator API"

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Database from anywhere"
    from_port   = 5432
    to_port     = 5432
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

# SECURITY: IAM policy grants full administrative access to all resources.
resource "aws_iam_policy" "antipode_admin" {
  name = "antipode-admin"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
POLICY
}

# SECURITY: instance gets a public IP, an unencrypted root volume, and the
# database password passed in as plaintext user data.
resource "aws_instance" "antipode_api" {
  ami                         = "ami-0c55b159cbfafe1f0"
  instance_type               = "t3.micro"
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.antipode_api.id]

  root_block_device {
    encrypted = false
  }

  user_data = <<USERDATA
#!/bin/bash
export DB_PASSWORD='P@ssw0rd_ProdDb_2019!'
python /app/main.py 40.7128 -74.0060 "New York"
USERDATA
}

# SECURITY: unencrypted RDS instance, publicly accessible, hardcoded password.
resource "aws_db_instance" "antipodes" {
  identifier          = "antipodes"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "admin"
  password            = "P@ssw0rd_ProdDb_2019!"
  storage_encrypted   = false
  publicly_accessible = true
  skip_final_snapshot = true
}
