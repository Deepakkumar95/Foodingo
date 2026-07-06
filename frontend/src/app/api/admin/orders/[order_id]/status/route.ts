import { NextResponse } from "next/server";

const BACKEND =
  process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function POST(
  req: Request,
  context: { params: { order_id: string } | Promise<{ order_id: string }> }
) {
  try {
    const auth = req.headers.get("authorization");
    const { order_id } = await context.params;
    const body = await req.json();

    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (auth) {
      headers.Authorization = auth;
    }

    const res = await fetch(`${BACKEND}/admin/orders/${order_id}/status`, {
      method: "POST",
      headers,
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
