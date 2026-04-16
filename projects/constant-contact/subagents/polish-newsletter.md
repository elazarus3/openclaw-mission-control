# Polish Newsletter

## Task
Take the assembled newsletter draft and apply strict formatting and HTML styling based on Dr. Lazarus's specifications. You must also write a customized intro and outro that vary based on the current month and season.

## Responsibilities
1. **Dynamic Intro & Outro:** 
   - **Intro:** Write a warm, professional, and personalized introduction from Dr. Ethan Lazarus. It MUST explicitly mention the current month and tie into the current season/lifestyle in Colorado (e.g., getting ski gear ready in winter, hiking/biking in spring, changing leaves in fall). Make it unique every time. **ADDITIONALLY, include a sentence or two briefly summarizing this month's content/articles.**
   - **Research Feed Section:** Include the "Want more updates?" section linking to the research feed with background `#F4F8FA` and the blue button (`#0083BB`).
   - **Outro / Come Back Section:** Include a strong, supportive call-to-action to book a return visit, matching the "Thinking about coming back? We'd love to see you." messaging. Background `#0C699D`, text `#ffffff`, white button with blue text (`#0C699D`). Emphasize that CNC is a "judgment-free zone". **CRITICAL: The link for the 'Book my Return Visit' button must be exactly: `https://www.clinicalnutritioncenter.com/contact-us`**
   - **Footer:** Center the phone number `(303) 750-9454`.
2. **Mobile-Responsive HTML (CRITICAL FIX):** The previous design squeezed text on mobile phones because it used fixed-width table columns. 
   - **DO NOT use fixed-width tables (`<td style="width: 150px;">`) side-by-side for text and images.**
   - Instead, use a wrapped fluid layout. For the intro image of Dr. Lazarus, use a left-aligned floating image: `<img src="https://www.clinicalnutritioncenter.com/wp-content/uploads/2026/02/Ethan-Lazarus-MD-Weight-Loss-Doctor-Denver-e1770407330388.jpg" align="left" style="width: 100%; max-width: 150px; height: auto; margin: 0 20px 10px 0; border-radius: 4px; display: block;">`. This allows text to naturally wrap underneath the image on narrow phone screens.
   - For all article blocks, alternate the background colors for contrast (e.g., `#ffffff` for the first, `#F4F8FA` for the second, and repeat).
   - For all article images, use fluid alignment with margins. Alternate the image alignment (`align="right"` with `margin-left: 20px`, then `align="left"` with `margin-right: 20px`) for each article. Use `style="width: 35%; max-width: 200px; height: auto; margin-bottom: 15px; border-radius: 4px; display: block;"`. This ensures text wraps nicely on mobile without being squeezed.
3. **Brand Styling:**
   - **Outer Body Background:** `#C9E5F5`
   - **Main Container:** Max-width `640px`, centered (`margin: 0 auto;`), white background, `border: 10px solid #0C699D`.
   - **Date Ribbon:** `<div style="background-color: #0C699D; padding: 10px 20px; text-align: center;"><p style="color: #ffffff; margin: 0;">[Month, Year]</p></div>`
   - **Title Banner:** `<div style="background-color: #DDE7ED; padding: 15px 20px; text-align: center;"><h1 style="color: #0C699D; margin: 0;">News from Clinical Nutrition Center</h1></div>`
   - **Intro Section Background:** `#DDE7ED`
   - **Section Headers (e.g., Medical Updates):** `<div style="background-color: #0C699D; padding: 15px 20px; text-align: center;"><h2 style="color: #ffffff; margin: 0;">Medical Updates & News</h2></div>`
   - **Typography:** Arial, Helvetica, sans-serif; Text color `#403F42`; Line-height `1.5`.

## Output
- Return ONLY the final, complete HTML string (starting with `<!DOCTYPE html>`). Do not wrap in markdown code blocks.