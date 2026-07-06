import { NextResponse } from "next/server";

const BACKEND =
  process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function GET(req: Request) {
  try {
    const auth = req.headers.get("authorization");

    const getHeaders: Record<string, string> | undefined = auth
      ? { Authorization: auth }
      : undefined;

    const res = await fetch(`${BACKEND}/orders`, {
      method: "GET",
      headers: getHeaders,
    });

    const text = await res.text();
    const contentType = res.headers.get("content-type") || "application/json";

    return new NextResponse(text, {
      status: res.status,
      headers: { "Content-Type": contentType },
    });
  } catch (err: any) {
    return new NextResponse(JSON.stringify({ error: String(err) }), { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const auth = req.headers.get("authorization");

    const postHeaders: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (auth) {
      postHeaders["Authorization"] = auth;
    }

    const res = await fetch(`${BACKEND}/orders`, {
      method: "POST",
      headers: postHeaders,
      body: JSON.stringify(body),
    });

    const text = await res.text();
    const contentType = res.headers.get("content-type") || "application/json";

    return new NextResponse(text, {
      status: res.status,
      headers: { "Content-Type": contentType },
    });
  } catch (err: any) {
    return new NextResponse(JSON.stringify({ error: String(err) }), { status: 500 });
  }
}
