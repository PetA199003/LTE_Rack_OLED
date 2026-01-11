# Dependency Analysis and Recommendations

## Project Overview
LTE Rack OLED Display - Raspberry Pi Zero project for monitoring RUT241 router via SNMP with a 2.23" Waveshare OLED display.

## Executive Summary
This document provides a comprehensive dependency analysis and recommendations for building a secure, maintainable, and efficient monitoring system.

---

## Recommended Core Dependencies

### Python Dependencies (requirements.txt)

#### Essential Libraries (Minimal Set)
```
# SNMP Client
pysnmp-lextudio==5.1.0         # Maintained fork of pysnmp (original is abandoned)
pyasn1==0.5.1                   # Required by pysnmp

# OLED Display Driver
Pillow==10.2.0                  # Image processing for OLED
luma.oled==3.13.0               # Waveshare OLED display driver
smbus2==0.4.3                   # I2C communication (if needed)
spidev==3.6                     # SPI communication (if needed)
```

#### Alternative SNMP Options
```
# Option 1: easysnmp (faster, C-based)
easysnmp==0.2.6                 # Requires net-snmp system library
                                 # Pro: Faster, more memory efficient
                                 # Con: System dependencies required

# Option 2: puresnmp (pure Python, simpler)
puresnmp==2.0.0                 # Pure Python implementation
                                 # Pro: No system dependencies
                                 # Con: Slower than C-based alternatives
```

---

## Security Analysis

### Current Vulnerabilities Assessment
**Status**: ✅ No dependencies exist yet

### Security Recommendations

#### 1. Use Latest Stable Versions
- All recommended versions above are current as of January 2025
- Pillow 10.2.0 includes security fixes for image processing vulnerabilities
- pysnmp-lextudio is the maintained fork (original pysnmp is deprecated)

#### 2. Known Vulnerabilities to Avoid
```
❌ pysnmp < 4.4.12              # Multiple CVEs, project abandoned
❌ Pillow < 10.0.0               # CVE-2023-44271, CVE-2023-50447
❌ luma.oled < 3.0.0             # Outdated, lacks security updates
```

#### 3. Security Best Practices
- Use virtual environment to isolate dependencies
- Pin exact versions in requirements.txt
- Regular security audits with `pip-audit` or `safety`
- Implement SNMP v3 with authentication (not v1/v2c)
- Store credentials in environment variables, never in code

---

## Dependency Bloat Analysis

### Minimalist Approach (Recommended)
**Total Dependencies**: 5-7 packages
**Installation Size**: ~50-80 MB

```
pysnmp-lextudio==5.1.0
pyasn1==0.5.1
Pillow==10.2.0
luma.oled==3.13.0
```

### Bloat to Avoid

#### ❌ Unnecessary Heavy Frameworks
```
# DON'T USE unless specifically needed:
numpy                           # Not needed for simple display rendering
pandas                          # Overkill for simple data processing
matplotlib                      # Too heavy for embedded systems
flask/django                    # Not needed for standalone display
```

#### ❌ Redundant Libraries
```
# Choose ONE SNMP library, not multiple:
pysnmp-lextudio    # Recommended
OR easysnmp        # Alternative
OR puresnmp        # Alternative
# Don't install more than one!
```

---

## System Dependencies

### Required OS Packages (Raspberry Pi OS)
```bash
# For Python development
sudo apt-get install python3-pip python3-venv

# For I2C/SPI (OLED display)
sudo apt-get install python3-dev i2c-tools

# For easysnmp (only if using easysnmp)
sudo apt-get install libsnmp-dev snmp-mibs-downloader

# Enable I2C/SPI interfaces
sudo raspi-config
# Interface Options -> I2C/SPI -> Enable
```

---

## Outdated Package Analysis

### Packages to Avoid (Deprecated/Unmaintained)

#### ❌ pysnmp (original)
- **Status**: Abandoned since 2019
- **Replacement**: pysnmp-lextudio
- **Risk**: No security updates, compatibility issues

#### ❌ python-snmp
- **Status**: Outdated
- **Replacement**: pysnmp-lextudio or easysnmp
- **Risk**: Limited functionality

#### ❌ luma.core < 2.0
- **Status**: Old version
- **Replacement**: Latest luma.oled (includes updated core)
- **Risk**: Missing features, potential bugs

---

## Performance Optimization

### Memory-Constrained Environment (Pi Zero)

#### Resource Usage Comparison
| Library | Memory | CPU | Installation Size |
|---------|--------|-----|-------------------|
| pysnmp-lextudio | ~30MB | Medium | 15MB |
| easysnmp | ~10MB | Low | 5MB |
| puresnmp | ~20MB | Medium | 8MB |

#### Recommendations for Pi Zero (512MB RAM)
1. **Use easysnmp** if performance is critical
2. **Use pysnmp-lextudio** for better compatibility
3. **Avoid** installing development tools in production
4. **Enable** Python optimization (`python3 -OO`)

---

## Dependency Management Best Practices

### 1. Use Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### 2. Pin Dependencies
```bash
# After testing, freeze exact versions
pip freeze > requirements.txt
```

### 3. Regular Updates Strategy
```bash
# Check for outdated packages
pip list --outdated

# Use pip-review for safer updates
pip install pip-review
pip-review --interactive

# Security audit
pip install pip-audit
pip-audit
```

### 4. Development vs Production
```
# requirements.txt (production - minimal)
pysnmp-lextudio==5.1.0
pyasn1==0.5.1
Pillow==10.2.0
luma.oled==3.13.0

# requirements-dev.txt (development only)
pytest==7.4.3
black==24.1.1
flake8==7.0.0
pip-audit==2.6.3
```

---

## Recommended Project Structure

```
LTE_Rack_OLED/
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── .python-version          # Python version (3.11.x recommended)
├── config.env.example       # Configuration template
├── src/
│   ├── __init__.py
│   ├── snmp_client.py       # SNMP polling logic
│   ├── display_handler.py   # OLED display management
│   └── main.py              # Main application
├── tests/
│   └── test_snmp_client.py
└── README.md
```

---

## Security Hardening Checklist

- [ ] Use Python 3.11+ (latest security patches)
- [ ] Pin all dependencies to exact versions
- [ ] Use SNMP v3 with authentication
- [ ] Store credentials in environment variables
- [ ] Run pip-audit before deployment
- [ ] Use virtual environment
- [ ] Disable unnecessary system services
- [ ] Regular update schedule (monthly check)
- [ ] Implement logging for security events
- [ ] Use systemd service with restricted permissions

---

## Installation Guide

### Minimal Production Setup
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install dependencies
pip install pysnmp-lextudio==5.1.0 pyasn1==0.5.1 Pillow==10.2.0 luma.oled==3.13.0

# 4. Verify installation
pip list
pip-audit

# 5. Freeze dependencies
pip freeze > requirements.txt
```

### Performance-Optimized Setup (easysnmp)
```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y libsnmp-dev python3-dev

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install easysnmp==0.2.6 Pillow==10.2.0 luma.oled==3.13.0

# 4. Verify
pip list
```

---

## Cost-Benefit Analysis

### Storage Space
- **Minimal setup**: ~50 MB
- **Full development**: ~150 MB
- **With unnecessary bloat**: 300+ MB ❌

### Update Maintenance
- **Well-maintained dependencies**: 2-3 updates/year
- **Deprecated dependencies**: Security risks, no updates ❌

### Performance Impact
- **Optimized (easysnmp)**: <5% CPU, ~10MB RAM
- **Standard (pysnmp-lextudio)**: <10% CPU, ~30MB RAM
- **Bloated (with numpy/pandas)**: >20% CPU, 100MB+ RAM ❌

---

## Conclusion and Next Steps

### ✅ Recommended Action Plan

1. **Choose SNMP library** based on requirements:
   - Performance-critical: `easysnmp`
   - Maximum compatibility: `pysnmp-lextudio`
   - Simplicity: `puresnmp`

2. **Create requirements.txt** with pinned versions

3. **Set up virtual environment** for isolation

4. **Implement security best practices**:
   - SNMP v3 with authentication
   - Environment-based configuration
   - Regular security audits

5. **Establish update schedule**:
   - Monthly: Check for security advisories
   - Quarterly: Update dependencies
   - Annually: Major version upgrades

### 🎯 Key Takeaways

- **Zero dependencies** currently = clean slate opportunity
- **Minimize bloat** by choosing lightweight libraries
- **Prioritize security** with maintained, updated packages
- **Plan for maintenance** with proper dependency management
- **Optimize for Pi Zero** limited resources

### 📋 Implementation Priority

**High Priority** (Start here):
1. Create requirements.txt with core dependencies
2. Set up virtual environment
3. Install and test OLED display library
4. Implement SNMP polling with chosen library

**Medium Priority**:
5. Add development dependencies (testing, linting)
6. Implement security hardening
7. Create systemd service

**Low Priority**:
8. Performance optimization
9. Advanced monitoring features
10. Documentation expansion

---

## Questions to Consider

Before finalizing dependencies, decide:

1. **SNMP Version**: v2c (simple) or v3 (secure)?
2. **Display Refresh Rate**: How often to poll? (impacts library choice)
3. **Error Handling**: Simple restart or sophisticated recovery?
4. **Deployment**: Manual or automated updates?
5. **Monitoring**: Just display or also logging/alerts?

---

*Document Version: 1.0*
*Last Updated: 2026-01-11*
*Target Platform: Raspberry Pi Zero (ARMv6)*
*Python Version: 3.11+*
