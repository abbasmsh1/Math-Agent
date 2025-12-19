# Vercel Deployment Checklist

Use this checklist to ensure a smooth deployment to Vercel.

## Pre-Deployment

- [ ] All code is committed and pushed to Git repository
- [ ] `requirements.txt` includes all necessary dependencies
- [ ] `vercel.json` is configured correctly
- [ ] `.vercelignore` is set up (optional but recommended)
- [ ] Environment variables are documented

## Environment Variables Setup

Before deploying, prepare these environment variables:

- [ ] `MISTRAL_API_KEY` - Your Mistral AI API key
- [ ] `MISTRAL_MODEL` - Model to use (default: `mistral-medium-latest`)
- [ ] `MAX_TOKENS` - Optional (default: 2048)
- [ ] `TEMPERATURE` - Optional (default: 0.2)
- [ ] `TOP_P` - Optional (default: 0.95)
- [ ] `DEBUG` - Optional (default: False)

## Vercel Setup

- [ ] Create Vercel account or login
- [ ] Connect Git repository to Vercel
- [ ] Add all environment variables in Vercel dashboard
- [ ] Verify environment variables are set for all environments (Production, Preview, Development)

## Deployment

- [ ] Run `vercel` command (or deploy via dashboard)
- [ ] Wait for build to complete
- [ ] Check build logs for any errors
- [ ] Note the deployment URL

## Post-Deployment Testing

- [ ] Test health endpoint: `https://your-app.vercel.app/health`
- [ ] Test home page: `https://your-app.vercel.app/`
- [ ] Test PDF upload: `https://your-app.vercel.app/upload`
- [ ] Test problem solving: `https://your-app.vercel.app/solve`
- [ ] Check Vercel function logs for any errors
- [ ] Verify environment variables are accessible

## Common Issues

### Build Fails
- Check `requirements.txt` for correct package versions
- Verify Python version compatibility (3.9+)
- Check build logs in Vercel dashboard

### Runtime Errors
- Verify environment variables are set correctly
- Check function logs in Vercel dashboard
- Ensure all dependencies are in `requirements.txt`

### Timeout Errors
- Large PDFs may take longer to process
- Consider upgrading to Pro plan (60s timeout)
- Implement file size limits

### Module Not Found
- Verify all imports are correct
- Check that `api/index.py` has correct path setup
- Ensure project structure matches expected layout

## Monitoring

After deployment:

- [ ] Set up Vercel analytics (if needed)
- [ ] Monitor function logs regularly
- [ ] Set up error alerts (optional)
- [ ] Track API usage and costs

## Rollback Plan

If something goes wrong:

1. Go to Vercel dashboard
2. Navigate to Deployments
3. Find the last working deployment
4. Click "Promote to Production"

## Next Steps

- [ ] Set up custom domain (optional)
- [ ] Configure CORS if needed
- [ ] Set up rate limiting for production
- [ ] Implement monitoring and alerts
- [ ] Document API endpoints

