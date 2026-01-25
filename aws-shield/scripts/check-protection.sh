#!/bin/bash
# Check AWS Shield protection status for resources

echo "=== AWS Shield Protection Status ==="
echo ""

# Check Shield subscription status
echo "Shield Advanced Subscription:"
SUBSCRIPTION=$(aws shield describe-subscription 2>/dev/null || echo "NOT_SUBSCRIBED")
if [[ "$SUBSCRIPTION" == "NOT_SUBSCRIBED" ]]; then
    echo "  Status: Not subscribed to Shield Advanced"
    echo "  Shield Standard: Active (automatic)"
else
    echo "  Status: Shield Advanced Active"
    aws shield describe-subscription --query 'Subscription.{TimeCommitment:TimeCommitmentInSeconds,AutoRenew:AutoRenew}' --output table
fi

echo ""

# List protected resources (Shield Advanced only)
echo "Shield Advanced Protected Resources:"
PROTECTIONS=$(aws shield list-protections 2>/dev/null)
if [[ -z "$PROTECTIONS" ]] || [[ $(echo "$PROTECTIONS" | jq '.Protections | length') -eq 0 ]]; then
    echo "  No Shield Advanced protections configured"
    echo "  (Shield Standard is still active on eligible resources)"
else
    echo "$PROTECTIONS" | jq -r '.Protections[] | "  - \(.Name): \(.ResourceArn)"'
fi

echo ""

# List protection groups (Shield Advanced only)
echo "Protection Groups:"
GROUPS=$(aws shield list-protection-groups 2>/dev/null)
if [[ -z "$GROUPS" ]] || [[ $(echo "$GROUPS" | jq '.ProtectionGroups | length') -eq 0 ]]; then
    echo "  No protection groups configured"
else
    echo "$GROUPS" | jq -r '.ProtectionGroups[] | "  - \(.ProtectionGroupId): \(.Pattern)"'
fi

echo ""

# Check for recent DDoS attacks (Shield Advanced only)
echo "Recent Attack Activity (last 24 hours):"
START_TIME=$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

ATTACKS=$(aws shield list-attacks \
    --start-time "$START_TIME" \
    --end-time "$END_TIME" \
    2>/dev/null)

if [[ -z "$ATTACKS" ]] || [[ $(echo "$ATTACKS" | jq '.AttackSummaries | length') -eq 0 ]]; then
    echo "  No attacks detected"
else
    echo "$ATTACKS" | jq -r '.AttackSummaries[] | "  - Attack ID: \(.AttackId)\n    Resource: \(.ResourceArn)\n    Start: \(.StartTime)\n    End: \(.EndTime)"'
fi

echo ""
echo "=== Resources Automatically Protected by Shield Standard ==="
echo "  - All Elastic Load Balancers (ALB, NLB, CLB)"
echo "  - Amazon CloudFront distributions"
echo "  - Amazon Route 53 hosted zones"
echo "  - AWS Global Accelerator endpoints"
