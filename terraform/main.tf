resource "aws_ecr_repository" "api_club_repo" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "IMMUTABLE"
}

