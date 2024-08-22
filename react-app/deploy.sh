echo "Building"
npm run build
echo "Build complete"

echo "Deploying to server"
scp -r dist/* jordan@151.236.219.211:/var/www/icst/
echo "Deployed to server"