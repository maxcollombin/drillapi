# Use LOCAL_DEV=1 to run uvicorn for local deployment
FROM public.ecr.aws/lambda/python:3.14

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src/drillapi ./drillapi
COPY tests ./tests

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["drillapi.app.handler"]
