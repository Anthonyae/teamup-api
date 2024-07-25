#!/bin/sh

# Copy the .env file to .env.example
cp .env .env.example
# remove sensitive info
sed -i 's/=.*/=/' .env.example
# add header note
sed -i '1s/^/# generated automatically by .git\/hooks\/pre-commit\n/' .env.example

# Add a line to .gitignore to ignore the real .env file
if ! grep -q "^\.env$" .gitignore; then
  echo ".env" >> .gitignore
fi
