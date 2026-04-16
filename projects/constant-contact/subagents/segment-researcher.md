# Segment Researcher

## Task
Determine the newsletter's primary audience focus for this month and gather the context needed to write compelling content.

## Steps
1. Read `projects/constant-contact/orchestrator.md` to understand the workflow.
2. Read `projects/constant-contact/summarized_articles.json` (or similar) to see what blog content is available this month.
3. Check `projects/constant-contact/last_newsletter_date.txt` if it exists to determine if this is a "lapsed reactivation" month or an "active patient" month.
4. Make a decision:
   - **Every 3rd newsletter**: Lapsed patient reactivation focus (majority of list is lapsed)
   - **Other newsletters**: Active patient / clinical education focus
5. Write a brief `segment-context.json` to the run folder with:
   ```json
   {
     "primary_audience": "active | lapsed",
     "angle": "one sentence describing the month's angle",
     "featured_post": "the single best blog post to feature this month",
     "reactivation_hook": "the specific question or offer to bring lapsed patients back"
   }
   ```

## Model
minimax/MiniMax-M2.7
