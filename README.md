# LTE Rack OLED Display

Raspberry Pi Zero-based status display for monitoring RUT241 LTE router via SNMP on a 2.23" Waveshare OLED display.

## Features

- Real-time SNMP monitoring of LTE router status
- Displays signal strength, network type, operator, and connection state
- Optimized for Raspberry Pi Zero (minimal resource usage)
- Security-focused dependency management
- Support for SNMP v2c and v3

## Quick Start

### Prerequisites

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y python3 python3-pip python3-venv i2c-tools

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable
```

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd LTE_Rack_OLED

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure application
cp config.env.example config.env
nano config.env  # Edit with your settings
```

### Alternative: Performance-Optimized Installation

For better performance on Pi Zero (lower memory, faster execution):

```bash
# Install system dependency for easysnmp
sudo apt-get install -y libsnmp-dev

# Install performance-optimized dependencies
pip install -r requirements-performance.txt
```

## Dependency Management

### Security First

All dependencies are:
- ✅ Currently maintained and updated
- ✅ Free from known security vulnerabilities
- ✅ Minimal and purpose-specific
- ✅ Tested on Raspberry Pi Zero

### Dependency Choices

**SNMP Library**: `pysnmp-lextudio` (maintained fork)
- Original `pysnmp` is abandoned
- Security updates and Python 3.11+ support
- Alternative: `easysnmp` for performance (see requirements-performance.txt)

**Display Driver**: `luma.oled`
- Well-maintained, active community
- Supports Waveshare displays
- Efficient for embedded systems

**Image Processing**: `Pillow`
- Latest version with security patches
- Required for OLED rendering

### Regular Updates

```bash
# Check for outdated packages
pip list --outdated

# Security audit
pip install pip-audit
pip-audit

# Update dependencies (carefully)
pip install --upgrade pip-audit
pip-audit
```

## Project Structure

```
LTE_Rack_OLED/
├── requirements.txt              # Production dependencies (standard)
├── requirements-performance.txt  # Performance-optimized (alternative)
├── requirements-dev.txt          # Development tools
├── config.env.example            # Configuration template
├── .python-version              # Python 3.11.7
├── .gitignore                   # Git ignore rules
├── DEPENDENCY_ANALYSIS.md       # Detailed dependency audit
└── README.md                    # This file
```

## Configuration

Edit `config.env` with your settings:

```bash
# Basic SNMP v2c (simple)
SNMP_HOST=192.168.1.1
SNMP_COMMUNITY=public
SNMP_VERSION=2c

# Secure SNMP v3 (recommended for production)
SNMP_VERSION=3
SNMP_USER=your_username
SNMP_AUTH_PASSWORD=your_auth_password
SNMP_PRIV_PASSWORD=your_priv_password
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black .

# Linting
flake8 src/

# Security audit
pip-audit
```

## Troubleshooting

### I2C Not Working
```bash
# Check I2C devices
sudo i2cdetect -y 1

# If not found, ensure I2C is enabled
sudo raspi-config
```

### SNMP Connection Issues
```bash
# Test SNMP connection manually
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.1.0
```

### Memory Issues on Pi Zero
- Use `requirements-performance.txt` instead
- Reduce display update interval
- Disable unnecessary system services

## Security Recommendations

1. **Use SNMP v3** with authentication and encryption
2. **Never commit** `config.env` to version control
3. **Run regular audits** with `pip-audit`
4. **Keep dependencies updated** (monthly checks)
5. **Use virtual environment** for isolation
6. **Restrict file permissions** on config files

```bash
chmod 600 config.env
```

## Performance Optimization

For best performance on Raspberry Pi Zero:

1. Use `requirements-performance.txt` (easysnmp is faster)
2. Optimize Python execution: `python3 -OO your_script.py`
3. Set appropriate update intervals (5-10 seconds recommended)
4. Consider using systemd service with resource limits

## Documentation

For detailed dependency analysis, security considerations, and architectural decisions, see:
- [DEPENDENCY_ANALYSIS.md](DEPENDENCY_ANALYSIS.md) - Complete dependency audit and recommendations

## License

[Your License Here]

## Contributing

1. Follow dependency management guidelines in DEPENDENCY_ANALYSIS.md
2. Run security audit before submitting PRs
3. Keep dependencies minimal
4. Test on actual Raspberry Pi Zero hardware

## Support

For issues related to:
- **Dependencies**: See DEPENDENCY_ANALYSIS.md
- **Hardware**: Check Waveshare documentation
- **SNMP**: Refer to RUT241 documentation
- **General issues**: Open GitHub issue

---

**Last Updated**: 2026-01-11
**Target Platform**: Raspberry Pi Zero W/WH
**Python Version**: 3.11.7
**Status**: Ready for implementation
