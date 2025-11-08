pipeline {
    agent any

    environment {
        SONARQUBE = 'sonarqube'
        REGISTRY_URL = credentials('nexus-registry-url')
        #REGISTRY_USER = credentials('nexus-username')
        #REGISTRY_PASS = credentials('nexus-password')
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
                    sh '''
                    ${scannerHome}/bin/sonar-scanner \
                      -Dsonar.projectKey=ums-cicd \
                      -Dsonar.sources=. \
                      -Dsonar.host.url=$SONAR_HOST_URL \
                      -Dsonar.login=$SONAR_AUTH_TOKEN
                    '''
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
               withCredentials([usernamePassword(credentialsId: 'jenkins_nexus_sonarqube', usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) {
                    echo $NEXUS_PASS | docker login -u $NEXUS_USER --password-stdin $REGISTRY_URL

                    docker tag ums-auth-service:latest $REGISTRY_URL/ums-auth-service:$IMAGE_TAG
                    docker tag ums-user-service:latest $REGISTRY_URL/ums-user-service:$IMAGE_TAG
                    docker tag ums-frontend:latest $REGISTRY_URL/ums-frontend:$IMAGE_TAG

                    docker push $REGISTRY_URL/ums-auth-service:$IMAGE_TAG
                    docker push $REGISTRY_URL/ums-user-service:$IMAGE_TAG
                    docker push $REGISTRY_URL/ums-frontend:$IMAGE_TAG

                    docker logout $REGISTRY_URL
                    '''
                }
            }
        }

        stage('Upload Docker Compose File (Optional)') {
            steps {
                echo "📦 Uploading docker-compose.yml to Nexus raw repo..."
                withCredentials([usernamePassword(credentialsId: 'nexus-docker-cred', usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) {
                    sh '''
                    curl -u $NEXUS_USER:$NEXUS_PASS \
                         --upload-file docker-compose.yml \
                         http://$REGISTRY_URL/repository/ums-cicd-compose/docker-compose-${IMAGE_TAG}.yml
                    '''
                }
            }
        }

        stage('Deployment (Optional)') {
            steps {
                echo "⚙️  Deployment placeholder — can be configured to SSH into Docker host and pull latest images."
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
            echo "❌ Pipeline failed. Check logs for errors."
        }
    }
}

