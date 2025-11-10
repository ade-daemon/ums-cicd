pipeline {
    agent { label 'ums-agent' }  // Make sure your Jenkins agent node has this label

    environment {
        PYTHON_ENV = "venv"
        SONARQUBE = 'sonarqube' // Must match the name in Jenkins global config
        SONAR_HOST_URL = "http://192.168.56.23:9000" // IP of Manager VM SonarQube
        SONAR_PROJECT_KEY = "ums-cicd"
        NEXUS_REPO_URL = "http://192.168.56.23:8081/repository/ums/"
        BUILD_VERSION = "0.1.${BUILD_NUMBER}"
    }

    stages {
        stage('Setup Python Environment') {
            steps {
                echo "🔹 Setting up Python virtual environment..."
                sh '''
                python3 -m venv ${PYTHON_ENV}
                . ${PYTHON_ENV}/bin/activate
                pip install --upgrade pip setuptools wheel
                pip install -r requirements.txt
                '''
            }
        }

        stage('SonarQube Analysis') {
            environment {
                scannerHome = tool 'SonarQubeScanner'  // Must match tool name in Jenkins config
            }
            steps {
                echo "🔹 Running SonarQube static code analysis..."
                withSonarQubeEnv("${SONARQUBE}") {
                    sh '''
                    . ${PYTHON_ENV}/bin/activate
                    ${scannerHome}/bin/sonar-scanner \
                      -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                      -Dsonar.sources=. \
                      -Dsonar.host.url=${SONAR_HOST_URL} \
                      -Dsonar.login=${SONAR_AUTH_TOKEN}
                    '''
                }
            }
        }

        stage('Build Artifact') {
            steps {
                echo "🔹 Building UMS package version ${BUILD_VERSION}..."
                sh '''
                . ${PYTHON_ENV}/bin/activate
                python setup.py sdist
                echo "✅ Build complete. Artifacts:"
                ls -lh dist/
                '''
            }
        }

        stage('Upload to Nexus') {
            steps {
                echo "🔹 Uploading artifacts to Nexus..."
                withCredentials([usernamePassword(credentialsId: 'nexus-token', usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) {
                    sh '''
                    for file in dist/*; do
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
            sh 'rm -rf venv || true'
        }
    }
}


