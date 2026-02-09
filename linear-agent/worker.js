/**
 * Linear Agent Webhook Handler
 * 
 * Handles:
 * 1. OAuth callback for agent installation
 * 2. Webhooks when Limen is @mentioned or assigned issues
 * 3. Sends notifications to main session via Telegram
 */

// Configuration - will be set via wrangler secrets
// LINEAR_CLIENT_ID, LINEAR_CLIENT_SECRET, LINEAR_WEBHOOK_SECRET
// BOT_TOKEN, CHAT_ID

const BOT_TOKEN = "8436264291:AAFdQqsTT7EehEaWJWly2-73AtmpFT8-9Ww";
const CHAT_ID = "8574735426"; // Kartik's Telegram

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Health check
    if (path === "/" || path === "/health") {
      return new Response(JSON.stringify({ 
        status: "ok", 
        service: "linear-agent",
        timestamp: new Date().toISOString()
      }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    // OAuth callback
    if (path === "/callback") {
      return handleOAuthCallback(request, env, url);
    }

    // Webhook from Linear
    if (path === "/webhook" && request.method === "POST") {
      return handleWebhook(request, env);
    }

    // API endpoints for Limen to call
    if (path === "/api/create-issue" && request.method === "POST") {
      return handleCreateIssue(request, env);
    }

    if (path === "/api/update-issue" && request.method === "POST") {
      return handleUpdateIssue(request, env);
    }

    if (path === "/api/list-issues" && request.method === "GET") {
      return handleListIssues(request, env);
    }

    if (path === "/api/add-comment" && request.method === "POST") {
      return handleAddComment(request, env);
    }

    return new Response("Not found", { status: 404 });
  }
};

/**
 * Handle OAuth callback from Linear
 */
async function handleOAuthCallback(request, env, url) {
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  
  if (!code) {
    return new Response("Missing authorization code", { status: 400 });
  }

  try {
    // Exchange code for access token
    const tokenResponse = await fetch("https://api.linear.app/oauth/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        client_id: env.LINEAR_CLIENT_ID,
        client_secret: env.LINEAR_CLIENT_SECRET,
        redirect_uri: `${url.origin}/callback`,
        code: code,
      }),
    });

    if (!tokenResponse.ok) {
      const error = await tokenResponse.text();
      console.error("Token exchange failed:", error);
      return new Response(`Token exchange failed: ${error}`, { status: 500 });
    }

    const tokens = await tokenResponse.json();
    
    // Store tokens (in production, use KV or D1)
    // For now, log them and notify via Telegram
    console.log("OAuth tokens received:", JSON.stringify(tokens, null, 2));

    // Get the app's user ID in this workspace
    const viewerResponse = await fetch("https://api.linear.app/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${tokens.access_token}`,
      },
      body: JSON.stringify({
        query: `query { viewer { id name email } }`
      }),
    });

    const viewerData = await viewerResponse.json();
    const viewer = viewerData.data?.viewer;

    // Notify Kartik
    await sendTelegram(
      `✅ **Linear Agent Connected!**\n\n` +
      `Agent ID: ${viewer?.id || 'unknown'}\n` +
      `Name: ${viewer?.name || 'Limen'}\n\n` +
      `Access Token (save this!):\n\`${tokens.access_token}\`\n\n` +
      `Refresh Token:\n\`${tokens.refresh_token || 'none'}\``
    );

    return new Response(
      `<html><body style="font-family: sans-serif; padding: 40px;">
        <h1>✅ Linear Agent Connected!</h1>
        <p>Limen is now installed in your Linear workspace.</p>
        <p>You can close this window.</p>
        <p><strong>Next:</strong> Save the access token from Telegram to your secrets.</p>
      </body></html>`,
      { headers: { "Content-Type": "text/html" } }
    );

  } catch (error) {
    console.error("OAuth error:", error);
    return new Response(`OAuth error: ${error.message}`, { status: 500 });
  }
}

/**
 * Handle webhooks from Linear
 */
async function handleWebhook(request, env) {
  try {
    const payload = await request.json();
    console.log("Linear webhook received:", JSON.stringify(payload, null, 2));

    const { type, action, data } = payload;

    // Agent session events - when Limen is mentioned or assigned
    if (type === "AgentSession") {
      return handleAgentSession(action, data, env);
    }

    // Issue events
    if (type === "Issue") {
      return handleIssueEvent(action, data, env);
    }

    // Comment events
    if (type === "Comment") {
      return handleCommentEvent(action, data, env);
    }

    // Acknowledge other events
    return new Response(JSON.stringify({ ok: true }), {
      headers: { "Content-Type": "application/json" }
    });

  } catch (error) {
    console.error("Webhook error:", error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}

/**
 * Handle agent session events (mentions, assignments)
 */
async function handleAgentSession(action, data, env) {
  const session = data;
  const issue = session.issue;
  const prompt = session.promptContext || session.prompt;

  // Don't post generic ack — let the cron job handle real responses
  // (Generic ack was confusing the "has Limen responded?" check)

  let message = `🤖 **Linear Agent Session**\n\n`;
  message += `**Action:** ${action}\n`;
  
  if (issue) {
    message += `**Issue:** ${issue.title}\n`;
    message += `**ID:** ${issue.identifier || issue.id}\n`;
    message += `**URL:** ${issue.url || 'N/A'}\n`;
  }

  if (prompt) {
    message += `\n**Context:**\n${prompt.slice(0, 1000)}${prompt.length > 1000 ? '...' : ''}\n`;
  }

  message += `\n---\n`;
  message += `⚠️ **RESPOND IN LINEAR NOW** — Do not ask permission. Check the issue, understand the request, and reply directly in Linear.`;

  await sendTelegram(message);

  return new Response(JSON.stringify({ ok: true, processed: "agent_session" }), {
    headers: { "Content-Type": "application/json" }
  });
}

/**
 * Handle issue events
 */
async function handleIssueEvent(action, data, env) {
  // Only notify on significant events
  if (!["create", "update"].includes(action)) {
    return new Response(JSON.stringify({ ok: true }), {
      headers: { "Content-Type": "application/json" }
    });
  }

  const issue = data;
  
  // Check if Limen is assigned (delegate)
  // This would require knowing Limen's user ID
  
  let message = `📋 **Linear Issue ${action}d**\n\n`;
  message += `**Title:** ${issue.title}\n`;
  message += `**ID:** ${issue.identifier || issue.id}\n`;
  message += `**Priority:** ${issue.priority || 'None'}\n`;
  message += `**State:** ${issue.state?.name || 'Unknown'}\n`;

  if (issue.description) {
    message += `\n**Description:**\n${issue.description.slice(0, 500)}${issue.description.length > 500 ? '...' : ''}\n`;
  }

  await sendTelegram(message);

  return new Response(JSON.stringify({ ok: true, processed: "issue" }), {
    headers: { "Content-Type": "application/json" }
  });
}

/**
 * Handle comment events (mentions in comments)
 */
async function handleCommentEvent(action, data, env) {
  if (action !== "create") {
    return new Response(JSON.stringify({ ok: true }), {
      headers: { "Content-Type": "application/json" }
    });
  }

  const comment = data;
  
  // Check if Limen is mentioned in the comment body
  const body = comment.body || "";
  if (!body.toLowerCase().includes("limen") && !body.includes("@")) {
    return new Response(JSON.stringify({ ok: true }), {
      headers: { "Content-Type": "application/json" }
    });
  }

  // Don't respond to my own comments
  if (comment.user?.name === "Limen") {
    return new Response(JSON.stringify({ ok: true, skipped: "own_comment" }), {
      headers: { "Content-Type": "application/json" }
    });
  }

  // Don't post generic ack — let the cron job handle real responses
  // (Generic ack was confusing the "has Limen responded?" check)

  let message = `💬 **Linear Comment**\n\n`;
  message += `**Issue:** ${comment.issue?.title || 'Unknown'}\n`;
  message += `**ID:** ${comment.issue?.identifier || 'Unknown'}\n`;
  message += `**From:** ${comment.user?.name || 'Unknown'}\n\n`;
  message += `**Comment:**\n${body.slice(0, 800)}${body.length > 800 ? '...' : ''}\n`;
  message += `\n---\n`;
  message += `⚠️ **RESPOND IN LINEAR NOW** — Check the comment, understand what's being asked, and reply directly in Linear.`;

  await sendTelegram(message);

  return new Response(JSON.stringify({ ok: true, processed: "comment" }), {
    headers: { "Content-Type": "application/json" }
  });
}

/**
 * Post a comment to Linear
 */
async function postLinearComment(issueId, body, token) {
  try {
    const response = await fetch("https://api.linear.app/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({
        query: `mutation CreateComment($input: CommentCreateInput!) { commentCreate(input: $input) { success } }`,
        variables: { input: { issueId, body } }
      }),
    });
    
    if (!response.ok) {
      console.error("Linear comment failed:", await response.text());
    }
  } catch (error) {
    console.error("Linear comment error:", error);
  }
}

/**
 * API: Create issue
 */
async function handleCreateIssue(request, env) {
  const { title, description, teamId, priority, labelIds } = await request.json();
  const token = env.LINEAR_ACCESS_TOKEN;

  if (!token) {
    return new Response(JSON.stringify({ error: "No access token configured" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }

  const mutation = `
    mutation CreateIssue($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
          url
        }
      }
    }
  `;

  const response = await fetch("https://api.linear.app/graphql", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({
      query: mutation,
      variables: {
        input: {
          title,
          description,
          teamId,
          priority,
          labelIds,
        }
      }
    }),
  });

  const result = await response.json();
  return new Response(JSON.stringify(result), {
    headers: { "Content-Type": "application/json" }
  });
}

/**
 * API: Update issue
 */
async function handleUpdateIssue(request, env) {
  const { issueId, stateId, priority, title, description } = await request.json();
  const token = env.LINEAR_ACCESS_TOKEN;

  if (!token) {
    return new Response(JSON.stringify({ error: "No access token configured" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }

  const mutation = `
    mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue {
          id
          identifier
          title
          state { name }
        }
      }
    }
  `;

  const input = {};
  if (stateId) input.stateId = stateId;
  if (priority !== undefined) input.priority = priority;
  if (title) input.title = title;
  if (description) input.description = description;

  const response = await fetch("https://api.linear.app/graphql", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({
      query: mutation,
      variables: { id: issueId, input }
    }),
  });

  const result = await response.json();
  return new Response(JSON.stringify(result), {
    headers: { "Content-Type": "application/json" }
  });
}

/**
 * API: List issues assigned to Limen
 */
async function handleListIssues(request, env) {
  const token = env.LINEAR_ACCESS_TOKEN;

  if (!token) {
    return new Response(JSON.stringify({ error: "No access token configured" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }

  // Get issues assigned to the authenticated user (Limen)
  const query = `
    query MyIssues {
      viewer {
        assignedIssues(first: 50, filter: { state: { type: { nin: ["completed", "canceled"] } } }) {
          nodes {
            id
            identifier
            title
            description
            priority
            url
            state { name type }
            createdAt
            updatedAt
          }
        }
      }
    }
  `;

  const response = await fetch("https://api.linear.app/graphql", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({ query }),
  });

  const result = await response.json();
  return new Response(JSON.stringify(result), {
    headers: { "Content-Type": "application/json" }
  });
}

/**
 * API: Add comment to issue
 */
async function handleAddComment(request, env) {
  const { issueId, body } = await request.json();
  const token = env.LINEAR_ACCESS_TOKEN;

  if (!token) {
    return new Response(JSON.stringify({ error: "No access token configured" }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }

  const mutation = `
    mutation CreateComment($input: CommentCreateInput!) {
      commentCreate(input: $input) {
        success
        comment {
          id
          body
        }
      }
    }
  `;

  const response = await fetch("https://api.linear.app/graphql", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({
      query: mutation,
      variables: {
        input: { issueId, body }
      }
    }),
  });

  const result = await response.json();
  return new Response(JSON.stringify(result), {
    headers: { "Content-Type": "application/json" }
  });
}

/**
 * Send Telegram message
 */
async function sendTelegram(message) {
  try {
    const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: CHAT_ID,
        text: message,
        parse_mode: "Markdown",
      }),
    });

    if (!response.ok) {
      // Try without markdown if it fails
      await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: CHAT_ID,
          text: message,
        }),
      });
    }
  } catch (error) {
    console.error("Telegram send error:", error);
  }
}
