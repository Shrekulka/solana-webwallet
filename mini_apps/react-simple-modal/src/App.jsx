import {Html5Qrcode} from "html5-qrcode";
import React, {useEffect, useRef, useState} from "react";
import "./App.css";

function App() {
    const [qrBoxColor, setQrBoxColor] = useState("#ff0000");
    const qrCodeRef = useRef(null);
    const {Telegram} = window;

    useEffect(() => {
        const config = {
            fps: 10,
            qrbox: {width: 200, height: 200, borderColor: qrBoxColor},
        };

        const qrCodeSuccess = async (decodedText, decodedResult) => {
            setQrBoxColor("#00ff00");
            config.qrbox.borderColor = qrBoxColor; // Обновление цвета рамки

            // Подготовка данных для отправки
            const data = decodedText;

            // Проверка существования объекта Telegram
            if (Telegram && Telegram.WebApp) {
                // Отправка данных в Telegram
                try {
                    const sendDataSuccess = await Telegram.WebApp.sendData(
                        JSON.stringify(data)
                    );
                    if (!sendDataSuccess) {
                        throw new Error("Failed to send data to Telegram");
                    }
                    // Логирование успешной отправки данных
                    console.log("Data sent to Telegram:", data);
                } catch (error) {
                    // Логирование ошибки отправки данных
                    console.error("Error sending data to Telegram:", error);
                } finally {
                    // Закрытие камеры
                    qrCodeRef.current.stop().catch((err) => console.log("Scanner error"));
                    // Закрытие мини-приложения Telegram
                    Telegram.WebApp.close();
                }
            } else {
                console.error("Telegram or Telegram.WebApp is not available");
            }
        };

        qrCodeRef.current = new Html5Qrcode("qrCodeContainer");
        qrCodeRef.current.start({facingMode: "environment"}, config, qrCodeSuccess);

        return () => {
            if (qrCodeRef.current) {
                qrCodeRef.current.stop().catch((err) => console.log("Scanner error"));
            }
        };
    }, []);

    return (
        <div className="scaner">
            <div id="qrCodeContainer"/>
        </div>
    );
}

export default App;
