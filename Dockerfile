# We build on top of the an existing python image
FROM python:3.10.17-alpine
# This image comes with a /code folder where we should have our code
WORKDIR /code

# We install probaby more system libraries that actually need
RUN apk add --no-cache gcc musl-dev linux-headers postgresql postgresql-contrib libpq-dev bash
# For now we only copy pyproject.toml file to the docker image because we want to install all our Python libraries at this stage
COPY pyproject.toml pyproject.toml
RUN pip install -e .

# The entry point is called only when the container starts
 ENTRYPOINT ["./entrypoint.sh"]