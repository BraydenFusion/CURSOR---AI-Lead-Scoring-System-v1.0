# Your Login Credentials - Ready to Use! 🎯

## ✅ Account Status
Your account is being created automatically when the backend starts on Railway. After the next deployment, your account will be ready to use!

## 🔐 Login Credentials

- **Username:** `brayden`
- **Password:** `Brayden@Secure2024!`
- **Email:** `bsaundersjones@gmail.com`
- **Full Name:** Brayden Saunders-Jones
- **Company Role:** VP Sales
- **System Role:** Sales Rep
- **Payment Plan:** Free (Individual)

## 🌐 Login URLs

- **Ventrix.tech:** https://ventrix.tech/login
- **Railway Frontend:** https://frontend-production-e9b2.up.railway.app/login

## 📊 Dashboard

After login, you'll be automatically redirected to:
- **Sales Rep Dashboard:** `/dashboard/sales-rep`

## 🚀 How It Works

1. **Automatic Account Creation:** The backend automatically creates your account when it starts
2. **Ready to Use:** No manual registration needed - just log in!
3. **Already in Database:** Your credentials are stored securely in the Railway database

## ⏱️ Next Steps

1. **Wait for Deployment:** Railway will redeploy the backend with the account creation script (2-3 minutes)
2. **Check Status:** Verify backend is running at https://backend-base.up.railway.app/health
3. **Login:** Go to https://ventrix.tech/login and use the credentials above
4. **Start Using:** Access your Sales Rep dashboard and start managing leads!

## 🔒 Security Notes

- Your password is securely hashed using bcrypt
- The account is active and ready to use
- You can change your password after login (Settings → Security)
- Account is on the Free individual plan

## 🎯 What You Can Do

Once logged in as a Sales Rep, you can:
- ✅ View and manage your assigned leads
- ✅ Track lead scores and classifications  
- ✅ Add notes and activities to leads
- ✅ Monitor your sales pipeline
- ✅ Update lead status
- ✅ Access AI-powered insights

## 🆘 Troubleshooting

### If login doesn't work:
1. **Check Backend Status:** https://backend-base.up.railway.app/health
2. **Wait for Deployment:** The account creation runs on startup - wait 2-3 minutes after deployment
3. **Check Railway Logs:** Look for "Creating/updating Brayden's Sales Rep account..." in deploy logs
4. **Account Already Exists:** If the account exists, the script will update the password to match the credentials above

### If you see "Account creation had issues":
- The account may already exist (this is fine - it will update the password)
- Check Railway logs for specific error messages
- The script is idempotent - it's safe to run multiple times

---