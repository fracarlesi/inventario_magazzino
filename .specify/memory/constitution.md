<!--
SYNC IMPACT REPORT
==================
Version: 0.0.0 → 1.0.0
Rationale: Initial constitution for inventario_magazzino project

Modified Principles: N/A (initial creation)
Added Sections:
  - Core Principles (I-IV)
  - Data Integrity Requirements
  - Development Workflow
  - Governance

Removed Sections: N/A (initial creation)

Template Status:
  ✅ plan-template.md - Reviewed, constitution check compatible
  ✅ spec-template.md - Reviewed, requirements align with principles
  ✅ tasks-template.md - Reviewed, task structure supports principles
  ✅ agent-file-template.md - Reviewed, no updates needed
  ✅ checklist-template.md - Reviewed, no updates needed

Follow-up TODOs: None
-->

# Inventario Magazzino Constitution

## Core Principles

### I. Simplicity First
The system MUST remain simple and focused on core warehouse operations: tracking items in and out, displaying current inventory status. Every feature addition MUST be justified against this core purpose. Complexity that does not directly serve the single-user, single-shop use case MUST be rejected.

**Rationale**: This is a single-user tool for a car repair shop. Over-engineering with multi-tenancy, complex permissions, or enterprise features would add maintenance burden without value.

### II. Data Integrity (NON-NEGOTIABLE)
All inventory transactions MUST be recorded with complete traceability. The system MUST maintain an audit trail of all entries and exits. Data loss or corruption is unacceptable. Each transaction MUST capture: timestamp, item, quantity, operation type (in/out), and current stock level.

**Rationale**: Inventory accuracy is critical for business operations. Missing or incorrect data directly impacts shop operations and customer service.

### III. User-Centric Interface
The frontend interface MUST be intuitive enough for non-technical shop staff to use without training. Forms MUST be clear, validation messages MUST be helpful, and the current inventory view MUST be immediately understandable. The system MUST respond to user actions within 2 seconds under normal conditions.

**Rationale**: The target user is shop personnel focused on repairs, not IT specialists. The tool must be self-explanatory and fast to use during busy operations.

### IV. Single-Source Architecture
This is a single-user, single-shop system. The architecture MUST reflect this reality. Database design, authentication, and deployment MUST optimize for the single-user scenario. Multi-user features MUST NOT be implemented unless explicitly required and justified.

**Rationale**: Building for scale that won't exist wastes time and introduces unnecessary complexity. The system serves one shop with one user.

## Data Integrity Requirements

- All write operations MUST be atomic and transactional
- The system MUST validate all inputs before persisting to database
- Inventory quantities MUST be tracked as integers (no fractional items unless parts inventory requires it)
- Stock levels MUST NOT go negative without explicit warning
- Every transaction MUST be timestamped with server time (not client time)
- Database backups MUST be configured and documented in deployment instructions

## Development Workflow

- Code changes MUST include basic validation (manual testing or automated tests)
- Breaking changes to data models MUST include migration scripts
- Frontend changes MUST be tested in the target browser environment
- All configuration (database, API keys, etc.) MUST use environment variables, never hardcoded
- Deployment instructions MUST be maintained and tested

## Governance

This constitution establishes the architectural and quality standards for the Inventario Magazzino project. All feature decisions, code reviews, and implementation plans MUST align with these principles.

**Amendment Process**: Changes to this constitution require documentation of (a) what is changing, (b) why the change is necessary, and (c) impact on existing code/templates.

**Compliance**: All specifications, plans, and tasks generated through the /speckit commands MUST reference and comply with these principles. Any deviation MUST be explicitly justified in the complexity tracking section of the plan document.

**Simplicity Review**: Before implementing any feature, ask: "Does this serve the single-user car shop scenario?" If not, reject or simplify.

**Version**: 1.0.0 | **Ratified**: 2025-11-11 | **Last Amended**: 2025-11-11
