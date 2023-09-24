FROM openjdk:8-jdk-alpine

WORKDIR /app

COPY . .

RUN javac src/com/main/devOps/test/Main.java

CMD ["java", "src/com/main/devOps/test/Main.java", "input.txt"]
