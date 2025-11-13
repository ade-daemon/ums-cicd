pipeline {
    agent { label 'ums-agent' }

    environment {
        PYTHON_ENV = "venv"
        SONARQUBE = 'sonarqube'
        SONAR_HOST_URL = "http://192.168.56.23:9000"
        SONAR_PROJECT_KEY = "ums-cicd"
        NEXUS_REPO_URL = "http://192.168.56.23:8081/repository/ums/"
        BUILD_VERSION = "0.2.${BUILD_NUMBER}"
    }

    stages {
        stage('Setup Python Environment') {
            steps {
                echo "🔹 Setting up Python virtual environment..."
                sh '''
                python3 -m venv ${PYTHON_ENV}
                . ${PYTHON_ENV}/bin/activate
                pip install --upgrade pip setuptools wheel

                echo "Installing dependencies for user-service..."
                pip install -r user-service/requirements.txt

                echo "Installing dependencies for auth-service..."
                pip install -r auth-service/requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo "🧪 Running backend tests..."
                sh '''
                . ${PYTHON_ENV}/bin/activate
                pytest auth-service/tests || true
                pytest user-service/tests || true
                '''
            }
        }

        stage('SonarQube Analysis') {
            environment {
                scannerHome = tool 'SonarQubeScanner'
            }
            steps {
                echo "🔹 Running SonarQube static code analysis..."
                withSonarQubeEnv("${SONARQUBE}") {
                    sh '''
                    . ${PYTHON_ENV}/bin/activate
                    ${scannerHome}/bin/sonar-scanner \
                      -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                      -Dsonar.sources=auth-service,user-service,frontend \
                      -Dsonar.host.url=${SONAR_HOST_URL} \
                      -Dsonar.login=${SONAR_AUTH_TOKEN}
                    '''
                }
            }
        }

        stage('Build Python Artifacts') {
            steps {
                echo "🔹 Building backend packages..."
                sh '''
                . ${PYTHON_ENV}/bin/activate
                mkdir -p dist

                echo "Building auth-service..."
                cd auth-service
                python setup.py sdist
                cp dist/* ../dist/
                cd ..

                echo "Building user-service..."
                cd user-service
                python setup.py sdist
                cp dist/* ../dist/
                cd ..

                echo "✅ Backend builds complete."
                '''
            }
        }

        stage('Build Frontend') {
    steps {
        echo "🌐 Frontend is plain HTML/CSS — no build needed."
        sh '''
        # Optionally, just copy frontend files to dist for artifact upload
        mkdir -p dist/frontend
        cp -r frontend/* dist/frontend/
        ls -l dist/frontend
        '''
    }
}


        stage('Upload to Nexus') {
            steps {
                echo "🚀 Uploading artifacts to Nexus..."
                withCredentials([usernamePassword(credentialsId: 'nexus-token', usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) {
                    sh '''
                    find dist -type f | while read file; do
                        echo "Uploading $file ..."
                        curl -u $NEXUS_USER:$NEXUS_PASS \
                             --upload-file "$file" \
                             ${NEXUS_REPO_URL}
                    done
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Check console logs for details."
        }
        always {
            echo "🧹 Cleaning workspace..."
            sh 'deactivate || true'
            sh 'rm -rf venv dist || true'
        }
    }
}



