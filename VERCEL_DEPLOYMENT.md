# Vercel Deployment Guide

This guide will help you deploy the Math Agent System to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. A Mistral AI API key
3. Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### 1. Prepare Your Repository

Make sure your code is pushed to a Git repository (GitHub, GitLab, or Bitbucket).

### 2. Set Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add the following environment variables:

   ```
   MISTRAL_API_KEY=your_mistral_api_key_here
   MISTRAL_MODEL=mistral-medium-latest
   ```

   Optional variables:
   ```
   MAX_TOKENS=2048
   TEMPERATURE=0.2
   TOP_P=0.95
   DEBUG=False
   ```

4. Make sure to add these for **Production**, **Preview**, and **Development** environments

### 3. Deploy to Vercel

#### Option A: Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. For production deployment:
   ```bash
   vercel --prod
   ```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Vercel will automatically detect the Python project
4. Configure environment variables (see step 2)
5. Click **Deploy**

### 4. Verify Deployment

After deployment, Vercel will provide you with a URL like:
- `https://your-project-name.vercel.app`

Visit the URL to verify your application is working.

## Important Notes

### Serverless Function Limitations

Vercel serverless functions have some limitations:

1. **Execution Timeout**: 
   - Hobby plan: 10 seconds
   - Pro plan: 60 seconds
   - Enterprise: Custom

2. **Memory**: 
   - Default: 1024 MB
   - Can be increased in `vercel.json`

3. **File Size Limits**:
   - Request body: 4.5 MB (Hobby), 4.5 MB (Pro)
   - Consider limiting PDF file sizes

### Adjusting for Vercel

The application has been configured to work with Vercel:

- Configuration validation is lazy (only when needed)
- Static files are optional
- Templates are loaded from the correct path
- All dependencies are in `requirements.txt`

### Troubleshooting

#### Issue: "Module not found" errors

**Solution**: Make sure all dependencies are in `requirements.txt` and the Python version is compatible (3.9+).

#### Issue: "MISTRAL_API_KEY not found"

**Solution**: 
1. Check that environment variables are set in Vercel dashboard
2. Make sure they're set for the correct environment (Production/Preview/Development)
3. Redeploy after adding environment variables

#### Issue: Timeout errors

**Solution**:
- Large PDFs or complex problems may take longer
- Consider:
  - Upgrading to Pro plan for longer timeouts
  - Implementing async processing
  - Limiting PDF file sizes

#### Issue: Template not found

**Solution**: The templates directory should be at `app/templates/`. Make sure the directory structure is correct.

### Updating Dependencies

If you add new dependencies:

1. Update `requirements.txt`
2. Push to Git
3. Vercel will automatically rebuild on the next deployment

### Custom Domain

To use a custom domain:

1. Go to your project settings in Vercel
2. Navigate to **Domains**
3. Add your custom domain
4. Follow DNS configuration instructions

## Project Structure for Vercel

```
.
├── api/
│   └── index.py          # Vercel entry point
├── app/
│   ├── agents/
│   ├── core/
│   ├── services/
│   ├── templates/
│   └── main.py
├── vercel.json           # Vercel configuration
├── .vercelignore        # Files to ignore
├── requirements.txt     # Python dependencies
└── README.md
```

## Monitoring

Vercel provides built-in monitoring:

1. **Logs**: View function logs in the Vercel dashboard
2. **Analytics**: Monitor function performance
3. **Errors**: Track errors and exceptions

## Cost Considerations

- **Hobby Plan**: Free, but with limitations (10s timeout, 100GB bandwidth)
- **Pro Plan**: $20/month, better limits (60s timeout, 1TB bandwidth)
- **Enterprise**: Custom pricing

For production use with heavy traffic, consider the Pro plan.

## Next Steps

After deployment:

1. Test all endpoints
2. Monitor logs for any issues
3. Set up custom domain (optional)
4. Configure monitoring and alerts
5. Consider implementing rate limiting for production

## Support

For issues specific to:
- **Vercel**: Check [Vercel Documentation](https://vercel.com/docs)
- **This Application**: Check the main README.md

