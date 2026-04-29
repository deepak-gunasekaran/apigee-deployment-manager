#!/bin/bash

# Version management script for Apigee Deployment Manager
# Usage: ./scripts/version.sh [patch|minor|major|current]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to get current version
get_current_version() {
    local current_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    echo $current_tag
}

# Function to increment version
increment_version() {
    local version=$1
    local type=$2
    
    # Remove 'v' prefix if present
    version=${version#v}
    
    # Split version into components
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    local patch=$(echo $version | cut -d. -f3)
    
    case $type in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
        *)
            print_error "Invalid version type: $type"
            exit 1
            ;;
    esac
    
    echo "v${major}.${minor}.${patch}"
}

# Function to create and push tag
create_tag() {
    local new_version=$1
    
    print_info "Creating tag: $new_version"
    
    # Check if tag already exists
    if git rev-parse "$new_version" >/dev/null 2>&1; then
        print_error "Tag $new_version already exists!"
        exit 1
    fi
    
    # Create tag
    git tag -a "$new_version" -m "Release $new_version"
    
    # Push tag
    git push origin "$new_version"
    
    print_success "Tag $new_version created and pushed successfully!"
}

# Function to show version info
show_version_info() {
    local current_version=$(get_current_version)
    
    echo "=================================="
    echo "  Apigee Deployment Manager"
    echo "  Version Information"
    echo "=================================="
    echo "Current Version: $current_version"
    echo ""
    echo "Next versions would be:"
    echo "  Patch: $(increment_version $current_version patch)"
    echo "  Minor: $(increment_version $current_version minor)"
    echo "  Major: $(increment_version $current_version major)"
    echo ""
    echo "Docker Images:"
    echo "  Current: deepakdpk6/apigee-deployment-manager:${current_version#v}"
    echo "  Latest:  deepakdpk6/apigee-deployment-manager:latest"
    echo "=================================="
}

# Function to build Docker image locally
build_local() {
    local version=$1
    local build_date=$(date -u +'%Y%m%d')
    local commit_sha=$(git rev-parse --short HEAD)
    
    print_info "Building Docker image locally..."
    print_info "Version: $version"
    print_info "Build Date: $build_date"
    print_info "Commit SHA: $commit_sha"
    
    docker build \
        --build-arg BUILD_DATE="$build_date" \
        --build-arg BUILD_VERSION="$version" \
        --build-arg COMMIT_SHA="$commit_sha" \
        -t "deepakdpk6/apigee-deployment-manager:${version#v}" \
        -t "deepakdpk6/apigee-deployment-manager:latest" \
        .
    
    print_success "Docker image built successfully!"
    echo ""
    echo "To run the image:"
    echo "  docker run -d -p 5001:5000 deepakdpk6/apigee-deployment-manager:${version#v}"
}

# Main script logic
main() {
    local action=${1:-"current"}
    
    case $action in
        "current")
            show_version_info
            ;;
        "patch"|"minor"|"major")
            local current_version=$(get_current_version)
            local new_version=$(increment_version $current_version $action)
            
            print_info "Current version: $current_version"
            print_info "New version: $new_version"
            
            # Confirm action
            read -p "Create and push tag $new_version? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                create_tag $new_version
                
                # Ask if user wants to build locally
                read -p "Build Docker image locally? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    build_local $new_version
                fi
            else
                print_info "Operation cancelled."
            fi
            ;;
        "build")
            local current_version=$(get_current_version)
            build_local $current_version
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [patch|minor|major|current|build|help]"
            echo ""
            echo "Commands:"
            echo "  current  Show current version information (default)"
            echo "  patch    Increment patch version (x.x.X)"
            echo "  minor    Increment minor version (x.X.0)"
            echo "  major    Increment major version (X.0.0)"
            echo "  build    Build Docker image with current version"
            echo "  help     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 current    # Show version info"
            echo "  $0 patch      # Create v1.0.1 from v1.0.0"
            echo "  $0 minor      # Create v1.1.0 from v1.0.0"
            echo "  $0 major      # Create v2.0.0 from v1.0.0"
            echo "  $0 build      # Build Docker image locally"
            ;;
        *)
            print_error "Unknown command: $action"
            echo "Use '$0 help' for usage information."
            exit 1
            ;;
    esac
}

# Check if git is available
if ! command -v git &> /dev/null; then
    print_error "Git is required but not installed."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "This script must be run from within a git repository."
    exit 1
fi

# Run main function
main "$@"
