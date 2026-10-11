import { NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');

export async function POST(request: Request) {
  try {
    const { prompt } = await request.json();

    if (!process.env.GEMINI_API_KEY) {
      return NextResponse.json({ 
        success: true, 
        reply: "Yurt Al Asistanı (Demo Modu): Merhaba! MEB pansiyon mevzuatına göre akşam etüt saatimiz 19:15, gece yat yoklamamız ise 23:00'tür. 107, 207 ve 307 numaralı odalar depo ve idari alan olduğundan pansiyon konaklamasına kapalıdır. Size nasıl yardımcı olabilirim?" 
      });
    }

    const model = genAI.getGenerativeModel({ 
      model: 'gemini-1.5-flash',
      systemInstruction: 'Sen Millî Eğitim Bakanlığı (MEB) pansiyon mevzuatını, 19:15 etüt ve 23:00 yat yoklaması saatlerini, 107, 207 ve 307 nolu odaların depo olduğunu bilen uzman bir pansiyon asistanısın.'
    });

    const result = await model.generateContent(prompt);
    const responseText = result.response.text();

    return NextResponse.json({ success: true, reply: responseText });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}