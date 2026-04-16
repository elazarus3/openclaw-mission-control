# Fetch Articles

## Task
Use the `wordpress` skill to fetch all published blog posts from the previous calendar month. 

## Instructions
1. You MUST load the environment variables from the WordPress skill's `.env` file before executing the CLI.
2. Run the command like this:
   `cd /home/ethan/.openclaw/workspace/skills/wordpress && set -a; source .env; set +a; NODE_TLS_REJECT_UNAUTHORIZED=0 node scripts/wp-cli.js posts:list --query per_page=15 --query status=publish --query _embed=1 --query after=2026-03-01T00:00:00 --query before=2026-03-31T23:59:59`
   *(Adjust the 'after' and 'before' dates to match the previous calendar month).*

## CRITICAL FILTERING RULE
You MUST ONLY fetch standard blog posts that appear on the main news feed (`/news`). 
DO NOT fetch any posts from the Research feed. Research posts are typically stored as a custom post type (e.g., `research_update`) or under a specific research category. Ensure your WP-CLI query explicitly restricts the `post_type` to `post` (which is default for `posts:list`) and ignores research categories if possible, or filter them out from the JSON output.

## Output
Return a JSON array or structured list of the posts, including:
- Title
- URL / Link
- Published Date
- Excerpt or Content
- Featured Image URL (Extract this from the `_embedded["wp:featuredmedia"][0].source_url` field, or whatever path the embedded media URL is located in. DO NOT just return the numeric ID.)