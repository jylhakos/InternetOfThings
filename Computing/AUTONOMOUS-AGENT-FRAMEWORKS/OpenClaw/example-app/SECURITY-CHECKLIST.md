# Security Checklist for OpenClaw Deployment

## Pre-Deployment Security Checklist

### Environment and Configuration
- [ ] `.env` file created and contains valid API keys
- [ ] `.env` file has 600 permissions (owner read/write only)
- [ ] `.env` is in `.gitignore` and never committed to version control
- [ ] `RUN_AS_UID` and `RUN_AS_GID` set to non-root user (typically 1000:1000)
- [ ] All placeholder values replaced with real configuration
- [ ] Sensitive paths not mounted into container
- [ ] Config files reviewed for hardcoded secrets

### Docker Security
- [ ] Container runs as non-root user (verified in docker-compose.yml)
- [ ] Root filesystem set to read-only
- [ ] All capabilities dropped (`cap_drop: ALL`)
- [ ] `no-new-privileges` security option enabled
- [ ] Volumes mounted with minimal permissions (`:ro` where possible)
- [ ] Resource limits configured (CPU, memory)
- [ ] Health check configured and working
- [ ] Container restart policy set appropriately

### Network Security
- [ ] Gateway port bound to `127.0.0.1` only (not `0.0.0.0`)
- [ ] Firewall rules reviewed and configured
- [ ] No unnecessary ports exposed
- [ ] Network egress filtering considered/implemented
- [ ] If remote access needed: reverse proxy with TLS configured
- [ ] Strong SSL/TLS configuration (TLS 1.2+, strong ciphers)
- [ ] Certificate from trusted CA (Let's Encrypt)

### Authentication and Access Control
- [ ] Basic authentication enabled on reverse proxy
- [ ] Strong passwords in `.htpasswd` (if using Nginx auth)
- [ ] Consider additional authentication (OAuth, mutual TLS)
- [ ] SSH keys password-protected
- [ ] Access limited to necessary users/IPs only
- [ ] VPN considered for remote access

### Application Configuration
- [ ] Command whitelist defined and enforced
- [ ] Dangerous commands blocked or restricted
- [ ] File system access limited to workspace
- [ ] Maximum loop/iteration limits set
- [ ] Timeout values configured
- [ ] Only necessary plugins enabled
- [ ] Plugin sources verified and trusted

### Logging and Monitoring
- [ ] Logging enabled (`docker-compose.secure.yml`)
- [ ] Log retention configured
- [ ] Sensitive data redacted from logs
- [ ] Monitoring script tested (`./monitor.sh`)
- [ ] Alerts configured for security events
- [ ] Log aggregation considered (ELK, Loki, etc.)
- [ ] Regular log review process established

### Backup and Recovery
- [ ] Backup strategy defined
- [ ] Workspace backed up regularly
- [ ] Configuration backed up
- [ ] Recovery procedure documented and tested
- [ ] Backup encryption considered
- [ ] Off-site backup location

### Updates and Maintenance
- [ ] Update schedule defined
- [ ] Process for testing updates
- [ ] Rollback procedure documented
- [ ] Dependency scan scheduled (npm audit, pip-audit)
- [ ] Security advisories monitored
- [ ] Patch management process

### Testing and Validation
- [ ] Tested in non-production environment first
- [ ] Health check endpoints verified
- [ ] Error handling tested
- [ ] Security controls validated
- [ ] Performance tested under load
- [ ] Disaster recovery tested

### Documentation
- [ ] Architecture documented
- [ ] Security controls documented
- [ ] Incident response plan created
- [ ] Runbook for common operations
- [ ] Contact information for security issues
- [ ] Compliance requirements documented

## Post-Deployment Security Checklist

### Immediate (First 24 Hours)
- [ ] Verify container is running with correct user
- [ ] Check logs for errors or warnings
- [ ] Verify network connectivity
- [ ] Test health check endpoint
- [ ] Verify authentication working
- [ ] Check resource usage is normal
- [ ] Review initial security logs

### Weekly
- [ ] Review logs for suspicious activity
- [ ] Check for failed authentication attempts
- [ ] Verify backups completed successfully
- [ ] Review resource usage trends
- [ ] Check for available updates
- [ ] Scan for vulnerabilities

### Monthly
- [ ] Full security audit
- [ ] Review and update access controls
- [ ] Test disaster recovery procedures
- [ ] Review and rotate credentials
- [ ] Update documentation
- [ ] Review and test monitoring/alerting

### Quarterly
- [ ] Penetration testing (if applicable)
- [ ] Architecture review
- [ ] Compliance audit
- [ ] Review and update security policies
- [ ] Train team on security updates
- [ ] Review incident response plan

## Incident Response

### If Security Breach Suspected
1. **Contain**: Immediately stop the container
   ```bash
   docker compose -f docker-compose.secure.yml stop
   ```

2. **Preserve Evidence**: Copy logs before they rotate
   ```bash
   cp -r logs/ incident-logs-$(date +%Y%m%d-%H%M%S)/
   docker logs openclaw_secure > incident-docker-logs-$(date +%Y%m%d-%H%M%S).txt
   ```

3. **Investigate**: Review logs for:
   - Unauthorized access attempts
   - Unusual commands executed
   - Unexpected network connections
   - File modifications
   - Privilege escalation attempts

4. **Remediate**:
   - Rotate all API keys and credentials
   - Update to latest version
   - Apply security patches
   - Review and strengthen security controls
   - Change authentication credentials

5. **Document**: Record:
   - Timeline of events
   - Actions taken
   - Root cause analysis
   - Lessons learned
   - Preventive measures

6. **Notify**: If required:
   - Security team
   - Affected users
   - Compliance officers
   - Law enforcement (if applicable)

### Common Security Issues and Fixes

#### Issue: Port Exposed to Internet
```bash
# Check current binding
netstat -tuln | grep 18789

# Fix: Update docker-compose.secure.yml
# Change: "0.0.0.0:18789:18789"
# To: "127.0.0.1:18789:18789"

# Restart
docker compose -f docker-compose.secure.yml restart
```

#### Issue: Container Running as Root
```bash
# Check current user
docker exec openclaw_secure id

# Fix: Update docker-compose.secure.yml
# Set: user: "1000:1000"

# Rebuild and restart
docker compose -f docker-compose.secure.yml up -d --force-recreate
```

#### Issue: API Keys in Logs
```bash
# Fix: Update logging configuration
# Enable: redact_secrets: true
# Review and clean existing logs
sed -i 's/sk-[a-zA-Z0-9]\{32,\}/[REDACTED]/g' logs/*.log
```

## Security Resources

- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Docker Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

## Notes
- This checklist should be reviewed and updated regularly
- Not all items may apply to every deployment
- Adjust based on your specific security requirements and risk tolerance
- Document any deviations and their justifications
- Regular security reviews are essential for maintaining security posture
