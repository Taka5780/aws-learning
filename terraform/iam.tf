# Definition of the Roll Body
resource "aws_iam_role" "ec2_role" {
  name = "ec2-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

# Managed Policy Association
# For CloudWatch Agent (Sending Monitoring Data)
resource "aws_iam_role_policy_attachment" "cw_agent" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# For SSM (Accepting Command Execution from Lambda)
resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Creating an Instance Profile
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2-monitoring-profile"
  role = aws_iam_role.ec2_role.name
}
