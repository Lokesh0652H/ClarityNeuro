# Privacy & Data Handling

## Principles

1. **Local-first**: All inference runs locally. No MRI images are sent to external services.
2. **Minimal retention**: Uploaded images are stored temporarily for processing and deleted afterward.
3. **No credentials stored**: API tokens and credentials are never committed to the repository.
4. **Transparent metadata**: Only prediction metadata is persisted, not the original images.

## Data Flow

```
User uploads MRI → Temp storage → Preprocessing → Inference → Result saved to DB → Temp file deleted
```

## What IS Stored

| Data | Storage | Retention |
|------|---------|-----------|
| Prediction metadata | SQLite database | Until user deletes |
| Predicted class & probabilities | SQLite database | Until user deletes |
| Uncertainty metrics | SQLite database | Until user deletes |
| Grad-CAM++ heatmaps | Temporary files | Session only |
| Analysis timestamps | SQLite database | Until user deletes |
| Model metadata | SQLite database | Permanent |

## What is NOT Stored

| Data | Policy |
|------|--------|
| Original MRI images | Deleted after processing |
| Patient identifiers | Never collected |
| User credentials | Never stored in DB |
| IP addresses | Not logged by default |
| Diagnostic conclusions | Not generated |

## User Controls

- **Delete individual analysis**: `DELETE /api/history/{id}`
- **View all stored records**: `GET /api/history`
- **Export data**: CSV/JSON export of analysis metadata
- **Database location**: Local SQLite file (`neuroscan.db`)

## Security Measures

- Upload file size limits (configurable, default 10MB)
- Image format validation (JPEG, PNG only)
- Filename sanitization
- No execution of uploaded content
- CORS restricted to configured origins
- Environment-based configuration (no hardcoded secrets)
- Safe archive generation (no path traversal)

## Regulatory Disclaimer

This platform does NOT claim compliance with:
- HIPAA (Health Insurance Portability and Accountability Act)
- GDPR (General Data Protection Regulation)
- FDA medical device regulations
- CE marking requirements
- Any clinical trial or medical device regulatory framework

Users handling real patient data are responsible for ensuring compliance with applicable regulations in their jurisdiction.

## Recommendations for Production Use

If deploying with real patient data:
1. Add authentication and authorization
2. Encrypt the database
3. Implement audit logging
4. Configure HTTPS
5. Conduct a security review
6. Obtain appropriate regulatory guidance
7. Implement proper consent mechanisms
8. Add data retention policies compliant with local law
