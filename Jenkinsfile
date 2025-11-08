pipeline {
    agent any

    environment {
        SONARQUBE = 'sonarqube'
        REGISTRY_URL = credentials('REGISTRY_URL') 
        REGISTRY_URL_yaml = credentials('REGISTRY_URL_yaml')
        IMAGE_TAG = "build-${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo "🔹 Checking out UMS-CICD repository..."
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            environment {
                scannerHome = tool 'SonarQubeScanner'
            }
            steps {
                echo "🔹 Running static analysis..."
                withSonarQubeEnv("${SONARQUBE}") {
                    sh """
                    ${scannerHome}/bin/sonar-scanner \
                      -Dsonar.projectKey=ums-cicd \
                      -Dsonar.sources=. \
                      -Dsonar.host.url=${SONAR_HOST_URL} \
                      -Dsonar.login=${SONAR_AUTH_TOKEN}
                    """
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "🐳 Building Docker images for all services..."
                sh '''
                docker compose build
                '''
            }
        }

        stage('Push Images to Nexus Registry') {
            steps {
                echo "🚀 Pushing Docker images to Nexus Registry..."
                withCredentials([usernamePassword(
                    credentialsId: 'jenkins_nexus_sonarqube',
                    usernameVariable: 'NEXUS_USER',
                    passwordVariable: 'NEXUS_PASS'
                )]) {
                    sh """
                        echo "🔐 Logging in to Nexus Docker registry..."
                        echo "\$NEXUS_PASS" | docker login -u "\$NEXUS_USER" --password-stdin ${REGISTRY_URL}

                        echo "🏷️ Tagging images..."
                        docker tag ums-auth-service:latest ${REGISTRY_URL}/ums-auth-service:${IMAGE_TAG}
                        docker tag ums-user-service:latest ${REGISTRY_URL}/ums-user-service:${IMAGE_TAG}
                        docker tag ums-frontend:latest ${REGISTRY_URL}/ums-frontend:${IMAGE_TAG}

                        echo "📤 Pushing images to Nexus..."
                        docker push ${REGISTRY_URL}/ums-auth-service:${IMAGE_TAG}
                        docker push ${REGISTRY_URL}/ums-user-service:${IMAGE_TAG}
                        docker push ${REGISTRY_URL}/ums-frontend:${IMAGE_TAG}

                        echo "🚪 Logging out..."
                        docker logout ${REGISTRY_URL}
                    """
                }
            }
        }

        stage('Upload Docker Compose File (Optional)') {
            steps {
                echo "📦 Uploading docker-compose.yml to Nexus raw repo..."
                withCredentials([usernamePassword(
                    credentialsId: 'jenkins_nexus_sonarqube',
                    usernameVariable: 'NEXUS_USER',
                    passwordVariable: 'NEXUS_PASS'
                )]) {
                    sh """
                        echo "Uploading docker-compose.yml..."
                        curl -u "\$NEXUS_USER:\$NEXUS_PASS" \
                             --upload-file docker-compose.yml \
                             ${REGISTRY_URL_yaml}/docker-compose-${IMAGE_TAG}.yml
                    """
                }
            }
        }

        stage('Deployment (Optional)') {
            steps {
                echo "⚙️ Deployment placeholder — can SSH into Docker host to pull latest images later."
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up temporary Docker data..."
            sh '''
            docker image prune -af || true
            '''
        }

        success {
            echo "✅ CI/CD Pipeline for UMS completed successfully! Images pushed with tag: ${IMAGE_TAG}"
        }

        failure {
            echo "❌ Pipeline failed. Check logs for details."
        }
    }
}

