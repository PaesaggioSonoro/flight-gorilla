import express from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import cookieParser from "cookie-parser";
import dotenv from "dotenv";
import swaggerUi from "swagger-ui-express";
import {OpenApiGeneratorV3} from "@asteasolutions/zod-to-openapi";
import {registry} from "./config/openapi";
import {airportRouter} from "./apis/airport";
import {authRouter} from "./apis/auth";
import {userRouter} from "./apis/user";
import {flightRouter} from "./apis/flight";
import {locationRouter} from "./apis/location";
import {aircraftRouter} from "./apis/aircraft";
import {seatSessionRouter} from "./apis/seat_session";
import {searchRouter} from "./apis/search";
import {bookingRouter} from "./apis/booking";
import {airlineRouter} from "./apis/airline";
import {adminRouter} from "./apis/admin";


dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;


app.use(helmet());
app.use(cors({
  origin: ["http://localhost:4200","http://127.0.0.1:4200", "http://127.0.0.1", "http://localhost"],
  credentials: true,
  allowedHeaders: ["Content-Type", "Authorization", "X-CSRF-TOKEN"]
}));
app.use(morgan("combined"));
app.use(cookieParser());
app.use(express.json());
app.use(express.urlencoded({extended: true}));


app.get("/health", (req, res) => {
  res.status(200).json({status: "OK", timestamp: new Date().toISOString()});
});


app.use("/airports", airportRouter);
app.use("/auth", authRouter);
app.use("/user", userRouter);
app.use("/flight", flightRouter);
app.use("/location", locationRouter);
app.use("/aircraft", aircraftRouter);
app.use("/seat_session", seatSessionRouter);
app.use("/search", searchRouter);
app.use("/booking", bookingRouter);
app.use("/airline", airlineRouter);
app.use("/admin", adminRouter);


const generator = new OpenApiGeneratorV3(registry.definitions);
const document = generator.generateDocument({
  openapi: "3.0.0",
  info: {
    title: "Flight Gorilla API",
    version: "1.0.0",
    description: "Flight booking and management API",
  },
  servers: [
    {
      url: `http://localhost:${PORT}`,
      description: "Development server",
    },
  ],
});

app.use("/", swaggerUi.serve, swaggerUi.setup(document, {
  swaggerOptions: {
    deepLinking: false,
    displayOperationId: false,
    defaultModelsExpandDepth: 1,
    defaultModelExpandDepth: 1,
    docExpansion: "none",
    filter: false,
    showExtensions: false,
    showCommonExtensions: false,
    tryItOutEnabled: true
  }
}));


app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).json({error: "Something went wrong!"});
});


app.use("/{*any}", (req, res) => {
  res.status(404).json({error: "Route not found"});
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📚 API Documentation available at http://localhost:${PORT}/`);
});

export default app;
