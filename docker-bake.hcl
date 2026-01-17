# Docker Bake Configuration for NARRA_FORGE
# Forces colored output with progress bars

variable "BUILDKIT_PROGRESS" {
  default = "tty"
}

group "default" {
  targets = ["backend", "celery_worker", "celery_beat", "frontend"]
}

target "backend" {
  context = "."
  dockerfile = "Dockerfile"
  target = "production"
  tags = ["narra_forge-backend:latest"]
  output = ["type=docker"]
}

target "celery_worker" {
  context = "."
  dockerfile = "Dockerfile"
  target = "production"
  tags = ["narra_forge-celery_worker:latest"]
  output = ["type=docker"]
}

target "celery_beat" {
  context = "."
  dockerfile = "Dockerfile"
  target = "production"
  tags = ["narra_forge-celery_beat:latest"]
  output = ["type=docker"]
}

target "frontend" {
  context = "./frontend"
  dockerfile = "Dockerfile"
  target = "runner"
  tags = ["narra_forge-frontend:latest"]
  output = ["type=docker"]
}
