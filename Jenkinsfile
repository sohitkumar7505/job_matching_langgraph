pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.11'
        SONAR_HOST = 'http://sonarqube:9000' // Matches docker-compose service name if running in same network, or localhost:9000
        DOCKER_IMAGE = 'recruform-api'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements.txt
                    pip install ruff mypy bandit pip-audit pytest pytest-cov
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . .venv/bin/activate
                    ruff check src/ --output-format=json > ruff-report.json || true
                    ruff check src/ --show-fixes || true
                '''
            }
        }

        stage('Type Check') {
            steps {
                sh '''
                    . .venv/bin/activate
                    mypy src/ --ignore-missing-imports
                '''
            }
        }

        stage('Security Scan') {
            parallel {
                stage('Bandit') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            bandit -r src/ -f json -o bandit-report.json || true
                            bandit -r src/ -ll
                        '''
                    }
                }
                stage('Dependency Audit') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            pip-audit -r requirements.txt
                        '''
                    }
                }
                stage('Hadolint') {
                    steps {
                        sh 'hadolint Dockerfile || true'
                    }
                }
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest tests/ -v \\
                        --cov=src \\
                        --cov-report=xml:coverage.xml \\
                        --cov-report=html:htmlcov \\
                        --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        sonar-scanner \\
                            -Dsonar.projectKey=recruform \\
                            -Dsonar.sources=src/ \\
                            -Dsonar.python.coverage.reportPaths=coverage.xml \\
                            -Dsonar.host.url=$SONAR_HOST \\
                            -Dsonar.login=$SONAR_TOKEN
                    '''
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:$DOCKER_TAG .'
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                    trivy image \\
                        --severity HIGH,CRITICAL \\
                        --format json \\
                        --output trivy-report.json \\
                        $DOCKER_IMAGE:$DOCKER_TAG

                    trivy image \\
                        --severity HIGH,CRITICAL \\
                        --exit-code 0 \\
                        $DOCKER_IMAGE:$DOCKER_TAG

                    # Bonus: SBOM generation
                    trivy image --format cyclonedx --output sbom.json $DOCKER_IMAGE:$DOCKER_TAG
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.json,*.xml,htmlcov/**', allowEmptyArchive: true
        }
        success {
            echo '=== Pipeline PASSED ==='
        }
        failure {
            echo '=== Pipeline FAILED — check stage logs ==='
        }
        cleanup {
            sh 'docker rmi $DOCKER_IMAGE:$DOCKER_TAG || true'
        }
    }
}