pipeline {
  agent none

  environment {
    IMAGE_NAME = 'floodcast/floodcast-uv-image'
    GIT_REPO = 'https://github.com/insa-resq/floodcast.git'
    DOCKER_CREDS = 'floodcast'
    KUBECONFIG_CRED = 'kubernetes'
  }

  stages {

    stage('Checkout + Build + Push Image') {
      agent any

      steps {
        checkout([
          $class: 'GitSCM',
          branches: [[name: 'main']],
          userRemoteConfigs: [[url: env.GIT_REPO]]
        ])

        script {
          dockerImage = docker.build("${IMAGE_NAME}:${env.BUILD_NUMBER}")
        }

        script {
          docker.withRegistry('https://registry.hub.docker.com', DOCKER_CREDS) {
            dockerImage.push("${env.BUILD_NUMBER}")
            dockerImage.push("latest")
          }
        }
      }
    }

    stage('Deploy to Kubernetes') {
      agent {
        docker {
          image 'bitnami/kubectl:latest'
          // KEEP CONTAINER ALIVE
          args '--entrypoint=""'
        }
      }

      steps {
        withCredentials([file(credentialsId: KUBECONFIG_CRED, variable: 'KUBECONFIG')]) {
          sh '''
            echo "KUBECONFIG=$KUBECONFIG"
            kubectl version --client
            kubectl apply -f kubernetes_deployment.yaml
            kubectl apply -f ingress.yaml
            kubectl rollout status deployment/config-service
            kubectl rollout status deployment/flow-data-service
            kubectl rollout status deployment/gateway-service
            kubectl rollout status deployment/weather-data-service
            kubectl rollout status deployement/alert-service
          '''
        }
      }
    }
  }
}

