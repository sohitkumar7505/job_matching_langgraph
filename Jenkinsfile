pipeline {
    agent any

    environment {
        SONAR_HOST = 'http://localhost:9000'
        DOCKER_IMAGE = 'recruform-api'
    }

    stages {

        stage('Setup') {
            steps {
                sh '''
                python3 -m venv .venv
                . .venv/bin/activate
                pip install -r requirements.txt
                pip install pytest pytest-cov ruff mypy bandit pip-audit
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                . .venv/bin/activate
                ruff check . --fix
                '''
            }
        }

        stage('Type Check') {
            steps {
                sh '''
                . .venv/bin/activate
                mypy . --explicit-package-bases
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                . .venv/bin/activate
                bandit -r .
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                . .venv/bin/activate
                pytest --cov=src --cov-report=xml
                '''
            }
        }

        stage('Hadolint') {
            steps {
                sh 'hadolint Dockerfile'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                sh '''
                sonar-scanner \
                -Dsonar.login=YOUR_TOKEN
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t recruform-api .'
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                trivy image --severity HIGH,CRITICAL recruform-api
                '''
            }
        }
    }
}