pipeline {
    agent any

    stages {
        stage('Info') {
            steps {
                echo 'Name: Hitesh Sathvick'
                echo 'Roll No: 123456'
            }
        }

        stage('Run Python') {
            steps {
                sh 'python3 main.py'
            }
        }
    }
}
