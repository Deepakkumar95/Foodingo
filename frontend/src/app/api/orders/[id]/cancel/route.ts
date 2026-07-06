import { NextResponse } from "next/server";

const BACKEND =
  process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function POST(
  req: Request,
  context: { params: { id: string } | Promise<{ id: string }> }
) {
  try {
    const auth = req.headers.get("authorization");
    const { id } = await context.params;

    const res = await fetch(`${BACKEND}/orders/${id}/cancel`, {
      method: "POST",
      headers: auth ? { Authorization: auth } : undefined,
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
