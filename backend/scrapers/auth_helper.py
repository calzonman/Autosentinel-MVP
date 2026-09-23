import os
import sys
import time
import asyncio
from playwright.async_api import async_playwright

AUTH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "auth.json")

async def login_and_save_session(timeout_seconds: int = 180) -> dict:
    """
    Abre una ventana visible de navegador (headed) para que el usuario inicie
    sesión en Facebook Marketplace. Guarda las cookies de sesión en auth.json.
    """
    auth_file_path = os.path.abspath(AUTH_FILE)
    print(f"[Auth Helper] Iniciando ventana visible para Facebook Auth. Archivo de salida: {auth_file_path}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=["--disable-notifications", "--start-maximized"]
            )
            context = await browser.new_context(
                viewport=None,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            print("[Auth Helper] Navegando a Facebook Marketplace...")
            await page.goto("https://www.facebook.com/marketplace", wait_until="domcontentloaded")

            start_time = time.time()
            session_captured = False

            while time.time() - start_time < timeout_seconds:
                await asyncio.sleep(2)
                try:
                    # Si el usuario cierra el navegador manualmente
                    if page.is_closed() or not browser.is_connected():
                        print("[Auth Helper] Ventana cerrada por el usuario.")
                        break

                    cookies = await context.cookies()
                    # Verificar si existe cookie de sesión activa de Facebook ('c_user' o 'xs')
                    has_session_cookie = any(c['name'] in ('c_user', 'xs') for c in cookies)
                    
                    if has_session_cookie:
                        session_captured = True
                        await context.storage_state(path=auth_file_path)
                        print("[Auth Helper] ✅ Sesión de Facebook detectada. Guardado auth.json correctamente.")
                        await asyncio.sleep(1)
                        break

                except Exception as loop_err:
                    print(f"[Auth Helper Loop] {loop_err}")
                    break

            if not session_captured:
                try:
                    await context.storage_state(path=auth_file_path)
                    print("[Auth Helper] Estado guardado antes de cerrar.")
                except Exception:
                    pass

            try:
                await browser.close()
            except Exception:
                pass

            return {
                "success": session_captured or os.path.exists(auth_file_path),
                "auth_file": auth_file_path,
                "message": "Sesión guardada en auth.json" if session_captured else "Proceso finalizado"
            }

    except Exception as e:
        print(f"[Auth Helper Exception] {e}")
        return {"success": False, "error": str(e)}

def is_session_saved() -> bool:
    auth_path = os.path.abspath(AUTH_FILE)
    return os.path.exists(auth_path) and os.path.getsize(auth_path) > 50

if __name__ == "__main__":
    res = asyncio.run(login_and_save_session())
    print(res)
