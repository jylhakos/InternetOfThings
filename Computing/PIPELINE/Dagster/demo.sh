#!/bin/bash
# Complete Dagster BERT Pipeline Demo Script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} ${CYAN}$1${NC} ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Main demo function
main() {
    clear
    
    print_header "Dagster BERT Pipeline - Complete Demonstration"
    echo ""
    
    echo -e "${PURPLE}This demonstration shows:${NC}"
    echo "• Complete MLOps pipeline with Dagster orchestration"
    echo "• BERT model fine-tuning for text classification"  
    echo "• Local development and AWS production deployment"
    echo "• Comparison between Dagster and Apache Airflow"
    echo ""
    
    print_step "Project Structure Overview"
    echo ""
    cat << 'EOF'
dagster_project/
├── assets/bert_assets.py      # ML pipeline assets (data, training, evaluation)
├── resources/aws_resources.py # AWS resource configurations
├── jobs/bert_jobs.py          # Job definitions and scheduling
├── schedules/bert_schedules.py # Automated scheduling
└── __init__.py               # Main definitions

src/
├── bert_fine_tuning.py       # Core BERT training logic
├── minimal_bert.py           # Simplified BERT implementation
└── test_environment.py       # Environment testing

aws_config/
├── cloudformation-template.yaml  # Infrastructure as Code
└── ecs-task-definition.json      # Container definitions

Configuration Files:
├── dagster.yaml              # Dagster instance configuration
├── workspace.yaml            # Code location definitions
├── docker-compose.yml        # Multi-service deployment
├── requirements-dagster.txt  # Pipeline dependencies
└── deploy_aws.sh            # AWS deployment automation
EOF
    
    echo ""
    print_step "Pipeline Architecture"
    echo ""
    cat << 'EOF'
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Prep     │───▶│   BERT Training  │───▶│   Evaluation    │
│ training_dataset│    │trained_bert_model│    │model_evaluation │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Inference Tests │◀───│   Deployment     │◀───│                 │
│ inference_tests │    │ deployed_model   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
EOF
    
    echo ""
    print_step "Available Commands"
    echo ""
    echo -e "${CYAN}Local Development:${NC}"
    echo "  ./setup_local.sh full     # Complete local setup"
    echo "  dagster dev -w workspace.yaml  # Start Dagster UI (http://localhost:3000)"
    echo "  python api.py             # Start API server (http://localhost:8000)"
    echo ""
    echo -e "${CYAN}Docker Deployment:${NC}"
    echo "  docker-compose up -d      # Start all services"
    echo "  docker-compose --profile production up -d  # Production with Nginx"
    echo ""
    echo -e "${CYAN}AWS Deployment:${NC}"
    echo "  ./deploy_aws.sh all       # Complete AWS deployment"
    echo "  ./deploy_aws.sh clean     # Clean up AWS resources"
    echo ""
    echo -e "${CYAN}Testing:${NC}"
    echo "  python test_dagster_setup.py  # Test pipeline setup"
    echo "  ./test_api.sh             # Test API endpoints"
    echo ""
    
    print_step "Dagster vs Airflow Analysis"
    echo ""
    cat << 'EOF'
┌─────────────────┬─────────────────┬─────────────────┐
│    Feature      │    Dagster      │    Airflow      │
├─────────────────┼─────────────────┼─────────────────┤
│ Architecture    │ Asset-centric   │ Task-centric    │
│ Data Lineage    │ Built-in        │ Manual setup    │
│ Type Safety     │ Strong typing   │ Dynamic         │
│ UI/UX           │ Modern          │ Traditional     │
│ Testing         │ Built-in        │ Manual          │
│ ML/AI Support   │ Excellent       │ Good            │
│ Community       │ Growing         │ Large           │
│ Learning Curve  │ Moderate        │ Steep           │
│ AWS Integration │ First-class     │ Via providers   │
│ Development     │ Hot reloading   │ Manual restart  │
└─────────────────┴─────────────────┴─────────────────┘
EOF
    
    echo ""
    print_step "AWS Architecture Components"
    echo ""
    echo -e "${CYAN}Core Services:${NC}"
    echo "• ECS Fargate - Container orchestration"
    echo "• RDS PostgreSQL - Metadata storage"
    echo "• S3 - Data and model storage"
    echo "• Application Load Balancer - Traffic routing"
    echo ""
    echo -e "${CYAN}Security & Monitoring:${NC}"
    echo "• VPC & Security Groups - Network isolation"
    echo "• Secrets Manager - Credential management"
    echo "• CloudWatch - Logging and monitoring"
    echo "• IAM Roles - Access control"
    echo ""
    
    print_step "Cost Estimates (Monthly)"
    echo ""
    echo -e "${CYAN}Development Setup:${NC} \$47-69/month"
    echo "• ECS Fargate (0.5 vCPU): \$15-25"
    echo "• RDS db.t3.micro: \$13-20"
    echo "• S3 Storage (10GB): \$1-2"
    echo "• Load Balancer: \$18-22"
    echo ""
    echo -e "${CYAN}Production Setup:${NC} \$119-166/month"
    echo "• ECS Fargate (2 vCPU): \$60-90"
    echo "• RDS db.t3.small: \$25-35"
    echo "• S3 Storage (100GB): \$3-5"
    echo "• Additional services: \$31-36"
    echo ""
    
    print_step "Key Benefits of This Implementation"
    echo ""
    echo -e "${GREEN}✓${NC} Complete MLOps pipeline with version control"
    echo -e "${GREEN}✓${NC} Asset-centric approach for better data lineage"
    echo -e "${GREEN}✓${NC} Built-in testing and validation framework"
    echo -e "${GREEN}✓${NC} Seamless local development to production deployment"
    echo -e "${GREEN}✓${NC} Auto-scaling and fault-tolerant infrastructure"
    echo -e "${GREEN}✓${NC} Cost-optimized AWS resource utilization"
    echo -e "${GREEN}✓${NC} Comprehensive monitoring and observability"
    echo -e "${GREEN}✓${NC} Security best practices with IAM and VPC"
    echo ""
    
    print_step "Recommendation: Dagster vs Airflow"
    echo ""
    echo -e "${YELLOW}Choose Dagster for:${NC}"
    echo "• New ML/AI pipeline projects"
    echo "• Asset-centric data workflows"
    echo "• Modern development experience"
    echo "• Strong data lineage requirements"
    echo "• Cloud-native deployments"
    echo ""
    echo -e "${YELLOW}Choose Airflow for:${NC}"
    echo "• Existing Airflow infrastructure"
    echo "• Traditional ETL workflows"
    echo "• Large community ecosystem"
    echo "• Extensive third-party integrations"
    echo "• Enterprise legacy requirements"
    echo ""
    
    print_step "Next Steps"
    echo ""
    echo "1. Run local setup: ${CYAN}./setup_local.sh full${NC}"
    echo "2. Explore Dagster UI: ${CYAN}http://localhost:3000${NC}"
    echo "3. Test API endpoints: ${CYAN}http://localhost:8000/docs${NC}"
    echo "4. Deploy to AWS: ${CYAN}./deploy_aws.sh all${NC}"
    echo "5. Customize for your use case"
    echo ""
    
    print_success "Dagster BERT Pipeline demonstration complete!"
    echo ""
    echo " Documentation available:"
    echo "  • README.md - Complete setup guide"
    echo "  • QUICKSTART.md - Quick start instructions"
    echo "  • ARCHITECTURE.md - Architecture diagrams"
    echo "  • COST.md - AWS cost breakdown"
    echo ""
    echo " This implementation demonstrates that ${GREEN}Dagster is an excellent choice${NC}"
    echo "   for modern ML/AI pipelines with its asset-centric approach, built-in"
    echo "   observability, and seamless cloud integration."
    echo ""
}

# Run demonstration
main "$@"
