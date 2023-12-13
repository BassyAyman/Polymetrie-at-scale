terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.0"
    }
  }
}
provider "kubernetes" {
  config_path = "~/.kube/config"
}
resource "kubernetes_namespace" "test" {
  metadata {
    name = "terraform-test"
  }
}
resource "kubernetes_deployment" "test" {
  metadata {
    name      = "my-polymetrie"
    namespace = kubernetes_namespace.test.metadata.0.name
  }
  spec {
    selector {
      match_labels = {
        app = "MyPolymetrieApp"
      }
    }
    template {
      metadata {
        labels = {
          app = "MyPolymetrieApp"
        }
      }
      spec {
        container {
          image = "igormel/polymetrie:1.2"
          name  = "polymetrie-container"
          port {
            container_port = 8080
          }
        }
      }
    }
  }
}
resource "kubernetes_service" "test" {
  metadata {
    name      = "polymetrie-service"
    namespace = kubernetes_namespace.test.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.test.spec.0.template.0.metadata.0.labels.app
    }
    type = "ClusterIP"
    port {
      port        = 80
      target_port = 8080
    }
  }
}