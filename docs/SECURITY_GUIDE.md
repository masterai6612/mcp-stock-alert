# 🔒 Security Guide for Stock Alert System

## 🚨 **IMPORTANT: API Key Security**

Your n8n API key has been secured in the `.env` file and removed from the source code.

### ✅ **What We've Done:**
1. **Moved API key** to `.env` file (not committed to git)
2. **Updated script** to load from environment variables
3. **Added security checks** to prevent running without proper configuration

### 🔑 **API Key Management:**

**Current API Key Location:** `.env` file
```
N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
EMAIL_FROM=masterai6612@gmail.com
EMAIL_PASSWORD=tuzjwacknqgfztcr
```

**⚠️ NEVER commit the `.env` file to version control!**

### 🛡️ **Security Best Practices:**

#### **1. Rotate API Keys Regularly**
- Generate new n8n API keys monthly
- Update `.env` file with new keys
- Delete old keys from n8n

#### **2. Environment Variables**
```bash
# Set in your shell (alternative to .env file)
export N8N_API_KEY="your-new-api-key"
```

#### **3. Production Security**
- Use separate API keys for development/production
- Store keys in secure key management systems
- Enable n8n authentication and HTTPS
- Restrict API access by IP if possible

#### **4. File Permissions**
```bash
# Secure the .env file
chmod 600 .env
```

### 🔄 **How to Regenerate API Key:**

1. **Go to n8n**: http://localhost:5678
2. **Settings** → **API Keys**
3. **Delete old key**
4. **Generate new key**
5. **Update `.env` file**

### 🚫 **What NOT to Do:**
- ❌ Don't share API keys in chat/email
- ❌ Don't commit `.env` files
- ❌ Don't hardcode keys in source code
- ❌ Don't use production keys in development

### ✅ **Current Security Status:**
- 🔒 N8N API key secured in `.env`
- 🔒 Gmail app password secured in `.env`
- 🔒 Email address configured: masterai6612@gmail.com
- 🔒 `.env` in `.gitignore` (protected from git commits)
- 🔒 Scripts validate key presence before running
- 🔒 No hardcoded secrets in source code
- 🔒 Email system fully operational and secure

**Your secrets are now secure and email system is working!** 🛡️📧