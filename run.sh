#!/bin/bash
# Initialize boolean variables
build_backend=false
build_frontend=false

# Function to display usage
usage() {
  echo "Usage: $0 [-b|--build-backend] [-f|--build-frontend]"
  exit 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -b|--build-backend)
      build_backend=true
      ;;
    -f|--build-frontend)
      build_frontend=true
      ;;
    *)
      echo "Unknown parameter: $1"
      usage
      ;;
  esac
  shift
done

if [ ! $build_backend -a ! $build_frontend ]; then
    build_backend = true
    build_frontend = true
fi

echo "Backend build: $build_backend"
echo "Frontend build: $build_frontend"

if $build_backend; then
  echo "Building backend..."
  
  pip3 uninstall -y vnav_acquisition
  pip3 install .
fi

if $build_frontend; then
  echo "Building frontend..."

  cd vnav_acquisition/front_app
  pnpm build
  cd ../..
fi



vnav_acquisition --setup setup.json

