# 🤖 OpenAI-Powered Lead Scoring

This system now supports **real AI-powered lead scoring** using OpenAI GPT-4!

## 🎯 Features

- **Intelligent Scoring**: Uses GPT-4 to analyze leads and provide nuanced scoring
- **Comprehensive Analysis**: Considers engagement, buying signals, demographics, and context
- **Automatic Insights**: Generates talking points, concerns, and opportunities
- **Fallback System**: Automatically falls back to rule-based scoring if OpenAI is unavailable

## 🔑 Setup

### 1. Add OpenAI API Key

**Local Development:**
```bash
cd backend
echo "OPENAI_API_KEY=sk-proj-..." >> .env
```

**Railway Deployment:**
1. Go to Railway dashboard → Backend service → Variables
2. Add new variable:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key
3. Redeploy

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

The `openai` package is already included in `requirements.txt`.

## 🚀 Usage

### Create Sample Leads with AI Scoring

```bash
cd backend
export OPENAI_API_KEY="sk-proj-..."
python create_sample_leads.py
```

This will create 10 diverse leads:
- **High-value enterprise leads** (HOT)
- **Active engagement leads** (HOT)
- **Referral leads** (WARM)
- **Cold leads** (COLD)
- **Various sources and locations**

### Automatic AI Scoring

When you create a lead via the API, it will automatically:
1. Try OpenAI scoring first (if API key is set)
2. Fall back to rule-based scoring if OpenAI fails

```python
from app.services.ai_scoring import calculate_overall_score

# Automatically uses OpenAI if available
result = calculate_overall_score(lead_id, db, use_openai=True)
```

## 📊 How It Works

### OpenAI Scoring Process

1. **Context Gathering**: Collects all lead data, activities, and engagement events
2. **AI Analysis**: Sends comprehensive context to GPT-4
3. **Scoring**: GPT-4 analyzes and returns:
   - Overall score (0-100)
   - Engagement score (0-100)
   - Buying signal score (0-100)
   - Demographic score (0-100)
   - Priority tier (HOT/WARM/COLD)
   - Confidence level (0.0-1.0)
   - Insights (talking points, concerns, opportunities)
4. **Storage**: Saves scores and insights to database

### Scoring Criteria

The AI considers:
- **Engagement**: Activity frequency, recency, email opens, website visits
- **Buying Signals**: Demo requests, pricing inquiries, form submissions
- **Demographics**: Location, source quality, company fit, industry
- **Context**: Lead source (referrals > organic > paid > cold)
- **Activity Patterns**: Recent activity scored higher than old activity

## 🎨 Customization Options

### Model Selection

Edit `backend/app/services/openai_scoring.py`:

```python
# Use GPT-4 Turbo (best quality, more expensive)
model = "gpt-4-turbo-preview"

# Use GPT-4 (good balance)
model = "gpt-4"

# Use GPT-3.5 Turbo (faster, cheaper, still good)
model = "gpt-3.5-turbo"
```

### Prompt Customization

Edit the prompt in `analyze_lead_with_openai()` to customize:
- Scoring weights
- Industry-specific criteria
- Company-specific factors

## 💰 Cost Considerations

### OpenAI Pricing (as of 2024)

- **GPT-4 Turbo**: ~$0.01-0.03 per lead
- **GPT-3.5 Turbo**: ~$0.001-0.002 per lead

### Cost Optimization

1. **Use GPT-3.5 Turbo** for high-volume, lower-priority leads
2. **Use GPT-4** for high-value leads only
3. **Cache scores** - don't re-score unchanged leads
4. **Batch processing** - score multiple leads in one API call (future enhancement)

## 🔄 Fallback Behavior

The system automatically falls back to rule-based scoring if:
- `OPENAI_API_KEY` is not set
- OpenAI API is unavailable
- API rate limit is exceeded
- API call fails for any reason

This ensures the system continues working even if OpenAI is down.

## 📈 Future Enhancements

### Custom Model Training

For truly custom models trained specifically for your use case:

1. **Collect Training Data**: Export lead scores and outcomes
2. **Fine-tune OpenAI Model**: Use OpenAI's fine-tuning API
3. **Train Custom Model**: Use open-source models (BERT, RoBERTa) with your data
4. **Deploy**: Integrate custom model into scoring service

### Recommended Custom Training Approach

1. **Start with OpenAI**: Use GPT-4 to generate training data
2. **Collect Outcomes**: Track which leads convert and why
3. **Fine-tune**: Use OpenAI fine-tuning API with your data
4. **Cost Reduction**: Fine-tuned models are cheaper per inference

Or use open-source models:
- **BERT/RoBERTa**: Can be fine-tuned on your lead data
- **Requires**: Training infrastructure (GPU recommended)
- **Benefits**: No per-API-call costs, full control

## 🧪 Testing

```bash
# Test OpenAI scoring
cd backend
export OPENAI_API_KEY="sk-proj-..."
python -c "
from app.database import get_db
from app.services.ai_scoring import calculate_overall_score
from app.models.lead import Lead

with get_db() as db:
    lead = db.query(Lead).first()
    if lead:
        result = calculate_overall_score(lead.id, db, use_openai=True)
        print(f'Score: {result[\"overall_score\"]}/100')
        print(f'Tier: {result[\"priority_tier\"]}')
        print(f'Insights: {len(result[\"insights\"])} insights')
"
```

## 📝 Notes

- OpenAI API key is stored in environment variables only (never in code)
- All API calls are logged for debugging
- Scores are cached in database (don't re-score unnecessarily)
- Rate limiting: OpenAI has rate limits, system handles gracefully

---

**Status**: ✅ Ready to use  
**Next**: Set `OPENAI_API_KEY` and start creating leads!

