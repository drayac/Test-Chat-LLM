# 🔐 API Key Security Guide

## Overview
This guide shows you how to secure your Groq API key and avoid exposing it publicly on GitHub or other version control systems.

## 🚨 Why This Matters
- **Public exposure** = Anyone can use your API key and charge your account
- **Rate limiting** = Your app could be blocked if key is misused
- **Security compliance** = Required for professional deployments

## 🛡️ Security Methods

### Method 1: Environment Variables (Recommended)

**For Local Development:**
```bash
# Option A: Create .env file
echo "GROQ_API_KEY=your-actual-key-here" > .env

# Option B: Export in terminal
export GROQ_API_KEY="your-actual-key-here"

# Option C: Add to your shell profile (~/.bashrc, ~/.zshrc)
echo 'export GROQ_API_KEY="your-actual-key-here"' >> ~/.bashrc
```

**For Production Deployment:**

**Streamlit Cloud:**
1. Go to your app dashboard
2. Click "Settings" → "Secrets"
3. Add: `GROQ_API_KEY = "your-key-here"`

**Railway:**
```bash
railway add GROQ_API_KEY
# Enter your key when prompted
```

**Heroku:**
```bash
heroku config:set GROQ_API_KEY=your-key-here
```

**Docker:**
```bash
docker run -e GROQ_API_KEY=your-key-here your-app
```

**Vercel/Netlify:**
- Add environment variable in dashboard settings

### Method 2: Streamlit Secrets (Streamlit Cloud)

Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your-actual-key-here"
```

## 🔧 Quick Setup

1. **Run security setup:**
   ```bash
   chmod +x setup_security.sh
   ./setup_security.sh
   ```

2. **Edit .env file:**
   ```bash
   nano .env
   # Replace placeholder with your actual key
   ```

3. **Test locally:**
   ```bash
   ./launch_groq_app.sh
   ```

## ✅ Verification

The app will show warnings if you're using the demo key:
- Console: `⚠️ WARNING: Using demo API key...`
- Sidebar: `⚠️ Using demo API key. Set GROQ_API_KEY...`

## 🚀 Deployment Checklist

- [ ] API key stored as environment variable
- [ ] .env file added to .gitignore
- [ ] No hardcoded keys in source code
- [ ] Demo key warning appears when needed
- [ ] Production environment variables configured

## 🔒 Best Practices

1. **Never commit** API keys to version control
2. **Use different keys** for development/production
3. **Rotate keys regularly** (monthly recommended)
4. **Monitor usage** in Groq Console
5. **Set up alerts** for unusual activity
6. **Use least privilege** - only necessary permissions

## 🆘 If Key Gets Exposed

1. **Immediately revoke** the key in Groq Console
2. **Generate new key**
3. **Update all deployments**
4. **Check usage logs** for unauthorized activity
5. **Consider changing other secrets** if repository was compromised

## 📱 Platform-Specific Guides

### GitHub Actions
```yaml
env:
  GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
```

### Docker Compose
```yaml
environment:
  - GROQ_API_KEY=${GROQ_API_KEY}
```

### Kubernetes
```yaml
env:
- name: GROQ_API_KEY
  valueFrom:
    secretKeyRef:
      name: api-secrets
      key: groq-api-key
```

## 🏆 Security Achievement Unlocked!

Following this guide ensures your API key stays private and secure across all deployment scenarios. Your future self (and your wallet) will thank you! 🛡️✨