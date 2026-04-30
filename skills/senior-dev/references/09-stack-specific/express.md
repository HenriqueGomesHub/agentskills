# Express / Node.js Specific Guidance

Load this when working in Express, Node.js, or other Node-based backend frameworks (Fastify, Koa, Hono).

## Layer separation: the cardinal rule

A well-organized Express app has clear layers, each with a single responsibility:

```
Request flow:
HTTP → Route → Controller → Service → Repository → Database

Each layer's job:
- Route:       Map URL + method to a controller. Apply middleware (auth, validation).
- Controller:  Parse the request, call the service, format the response.
- Service:     Business logic. The thing that would still be true if you swapped HTTP for gRPC.
- Repository:  Database queries. The thing that would still be true if you swapped Postgres for MySQL.
```

**Why it matters:** when you mix layers, you can't test business logic without HTTP, you can't swap databases, and you can't reuse logic from a different entry point (a CLI script, a job queue, another service).

### What this looks like

```typescript
// routes/users.ts — just routing + middleware
router.post('/users', requireAuth, validate(createUserSchema), userController.create);

// controllers/userController.ts — request/response only
export const userController = {
  async create(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await userService.create(req.body);
      res.status(201).json(user);
    } catch (err) {
      next(err);
    }
  },
};

// services/userService.ts — business logic, no HTTP
export const userService = {
  async create(data: CreateUserData): Promise<User> {
    const existing = await userRepo.findByEmail(data.email);
    if (existing) throw new ConflictError('User already exists');
    const hashed = await hashPassword(data.password);
    return userRepo.insert({ ...data, password: hashed });
  },
};

// repositories/userRepo.ts — DB queries only, no business logic
export const userRepo = {
  async findByEmail(email: string): Promise<User | null> {
    return db.query('SELECT * FROM users WHERE email = $1', [email]).then(r => r.rows[0] ?? null);
  },
  async insert(data: NewUser): Promise<User> {
    return db.query('INSERT INTO users (...) VALUES (...) RETURNING *', [...]).then(r => r.rows[0]);
  },
};
```

The controller is 6 lines. The service has the logic. The repo has the SQL. Each layer is independently testable.

## Folder structure: feature-based

Same principle as React — organize by feature, not by type.

```
src/
├── features/
│   ├── users/
│   │   ├── userController.ts
│   │   ├── userService.ts
│   │   ├── userRepo.ts
│   │   ├── userSchema.ts          ← validation schemas
│   │   ├── userTypes.ts
│   │   ├── userRoutes.ts
│   │   └── index.ts                ← barrel export of routes
│   ├── orders/
│   │   └── ...
│   └── billing/
│       └── ...
├── middleware/                     ← cross-cutting middleware
│   ├── auth.ts
│   ├── errorHandler.ts
│   └── requestLogger.ts
├── lib/                            ← shared utilities
│   ├── db.ts
│   ├── logger.ts
│   └── crypto.ts
├── config/                         ← env + config
│   └── env.ts
└── server.ts                       ← composition root
```

`server.ts` wires it all together:

```typescript
import express from 'express';
import { userRoutes } from './features/users';
import { orderRoutes } from './features/orders';
import { errorHandler } from './middleware/errorHandler';

const app = express();
app.use(express.json());
app.use('/api/users', userRoutes);
app.use('/api/orders', orderRoutes);
app.use(errorHandler);  // must be last

app.listen(3000);
```

## Middleware discipline

Middleware should do **one thing**. Common middleware concerns:

- **Authentication** — verify the request is from a known user
- **Authorization** — verify that user is allowed to do this
- **Validation** — verify the request body/query/params match a schema
- **Logging** — record the request
- **Rate limiting** — throttle abusive clients
- **Error handling** — convert thrown errors into JSON responses

Don't combine concerns. A single `superMiddleware` that does auth + validation + logging is harder to reason about, harder to reorder, harder to skip selectively.

### Middleware order matters

```typescript
app.use(express.json());           // 1. Parse body so other middleware can read it
app.use(requestLogger);             // 2. Log every request
app.use('/api', rateLimiter);       // 3. Rate limit before auth (cheaper to reject)
app.use('/api', requireAuth);       // 4. Authenticate
app.use('/api/users', userRoutes);  // 5. Route handlers
app.use(errorHandler);              // 6. Error handler — MUST be last
```

The error handler must come last. Express identifies it by its 4-argument signature `(err, req, res, next)`.

## Validation at the boundary

**Always validate request data at the route level** before it reaches business logic. Use a schema validation library (Zod, Yup, Joi).

```typescript
// schemas/userSchema.ts
export const createUserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(128),
  name: z.string().min(1).max(100),
});

// middleware/validate.ts
export const validate = (schema: z.ZodSchema) =>
  (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.body);
    if (!result.success) return res.status(400).json({ errors: result.error.issues });
    req.body = result.data;  // sanitized, typed
    next();
  };

// route
router.post('/users', validate(createUserSchema), userController.create);
```

After this middleware, the controller and service can trust `req.body` is the right shape. No defensive checks needed downstream.

## Error handling: centralize it

One error handler at the bottom of the middleware stack. Everywhere else, just throw.

```typescript
// errors/AppError.ts
export class AppError extends Error {
  constructor(public status: number, message: string, public code?: string) {
    super(message);
  }
}
export class NotFoundError extends AppError { constructor(msg: string) { super(404, msg, 'NOT_FOUND'); } }
export class ConflictError extends AppError { constructor(msg: string) { super(409, msg, 'CONFLICT'); } }
export class ValidationError extends AppError { constructor(msg: string) { super(400, msg, 'VALIDATION'); } }

// middleware/errorHandler.ts
export function errorHandler(err: Error, req: Request, res: Response, next: NextFunction) {
  const errorId = generateId();

  if (err instanceof AppError) {
    logger.warn('handled_error', { errorId, status: err.status, code: err.code, path: req.path });
    return res.status(err.status).json({ error: { message: err.message, code: err.code, errorId } });
  }

  // Unknown error — log full details, return generic response
  logger.error('unhandled_error', { errorId, error: err, stack: err.stack, path: req.path });
  res.status(500).json({ error: { message: 'Internal server error', errorId } });
}
```

Now controllers stay clean:

```typescript
async create(req, res, next) {
  try {
    const user = await userService.create(req.body);
    res.status(201).json(user);
  } catch (err) {
    next(err);  // hands off to errorHandler
  }
}
```

Or use an `asyncHandler` wrapper to skip the try/catch boilerplate:

```typescript
export const asyncHandler = (fn: AsyncHandler) =>
  (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

router.post('/users', asyncHandler(userController.create));
```

## Async/await: forbid mixing patterns

Pick async/await and stick with it. Don't mix in callbacks, `.then()` chains, or `util.promisify` wrappers in your own code.

```typescript
// Bad — mixing
function handler(req, res) {
  userService.create(req.body)
    .then(user => res.status(201).json(user))
    .catch(err => {
      logger.error(err);
      res.status(500).json({ error: 'something' });
    });
}

// Good — async/await + central error handler
async function handler(req, res, next) {
  try {
    const user = await userService.create(req.body);
    res.status(201).json(user);
  } catch (err) {
    next(err);
  }
}
```

## Database concerns

### Use a query builder or ORM, not raw strings

Raw SQL with string concatenation is a SQL injection waiting to happen. Always parameterize.

```typescript
// CRIMINAL — SQL injection vulnerability
db.query(`SELECT * FROM users WHERE email = '${email}'`);

// Good — parameterized
db.query('SELECT * FROM users WHERE email = $1', [email]);

// Better — query builder (Knex, Kysely, Drizzle)
db.selectFrom('users').where('email', '=', email).executeTakeFirst();

// ORMs (Prisma, TypeORM) — type-safe by default
prisma.user.findUnique({ where: { email } });
```

### N+1 queries

The classic backend performance bug. Fetching a list, then querying once per item to load related data.

```typescript
// Bad — 1 + N queries
const orders = await db.query('SELECT * FROM orders');
for (const order of orders) {
  order.user = await db.query('SELECT * FROM users WHERE id = $1', [order.userId]);
}

// Good — 1 query with join
const orders = await db.query(`
  SELECT orders.*, users.name as user_name, users.email as user_email
  FROM orders LEFT JOIN users ON users.id = orders.user_id
`);

// Or with ORM eager loading
const orders = await prisma.order.findMany({ include: { user: true } });
```

When the list is paginated to 1000 items, the difference is 1 query vs 1001.

### Connection pooling

Always use a connection pool. Don't open a new DB connection per request.

```typescript
// Good — pool, configured once at startup
const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 20 });

// Use the pool everywhere
const result = await pool.query('SELECT * FROM users');
```

### Transactions

When multiple writes must succeed or fail together, use a transaction.

```typescript
await db.transaction(async (tx) => {
  await tx.query('UPDATE accounts SET balance = balance - $1 WHERE id = $2', [amount, fromId]);
  await tx.query('UPDATE accounts SET balance = balance + $1 WHERE id = $2', [amount, toId]);
  await tx.query('INSERT INTO transfers (from_id, to_id, amount) VALUES ($1, $2, $3)', [fromId, toId, amount]);
  // If anything throws, ALL three are rolled back
});
```

## Configuration and secrets

### Environment variables, validated

Don't read `process.env` scattered through the codebase. Read it once, validate it, export typed config.

```typescript
// config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.coerce.number().int().positive().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  STRIPE_API_KEY: z.string().startsWith('sk_'),
});

export const env = envSchema.parse(process.env);
// Now env.DATABASE_URL is typed and guaranteed to exist
```

If a required env var is missing, the app crashes at startup — not at the first request that needs it.

### Never commit secrets

`.env` files go in `.gitignore`. Use `.env.example` to document what env vars exist.

## Logging

Use a real logger, not `console.log`. Pino, Winston, or Bunyan.

```typescript
import pino from 'pino';
export const logger = pino({
  level: env.NODE_ENV === 'production' ? 'info' : 'debug',
  transport: env.NODE_ENV !== 'production' ? { target: 'pino-pretty' } : undefined,
});

// Use structured logging
logger.info({ userId: 123, action: 'login' }, 'user logged in');
logger.warn({ orderId: 456 }, 'order amount unusually high');
logger.error({ err, requestId }, 'request failed');
```

In production, structured JSON logs get shipped to an aggregator (Datadog, CloudWatch, ELK). They're searchable, filterable, alertable.

## Security: the minimums

For any production Express app:

- **HTTPS only.** Use `helmet` middleware. Set `Strict-Transport-Security`.
- **Rate limiting.** `express-rate-limit` on auth endpoints especially.
- **CORS configured explicitly.** Whitelist origins; don't `cors({ origin: '*' })` for an authenticated API.
- **CSRF protection** if you use cookies for auth.
- **Hash passwords with bcrypt or argon2.** Never store plaintext. Never use MD5/SHA1.
- **Don't put secrets in URLs.** Query strings get logged everywhere.
- **Validate file uploads.** Type, size, malware scan if relevant.
- **Set request body size limits.** `express.json({ limit: '10kb' })` for most APIs.
- **Don't expose stack traces** in production responses (your error handler should already handle this).
- **Keep dependencies updated.** `npm audit` regularly.

## Background jobs: don't run them in the request handler

If a request triggers a slow operation (sending email, generating a PDF, calling a third-party API), do it in a background job, not in the request handler.

```typescript
// Bad — request blocks for 3 seconds while email sends
async function signup(req, res) {
  const user = await userService.create(req.body);
  await emailService.sendWelcome(user.email);  // 3 seconds
  res.status(201).json(user);
}

// Good — request returns immediately; email happens async
async function signup(req, res) {
  const user = await userService.create(req.body);
  await jobQueue.enqueue('sendWelcomeEmail', { userId: user.id });
  res.status(201).json(user);
}
```

Use BullMQ, Inngest, or a managed queue. Don't try to invent your own.

## Common Express anti-patterns

- **Massive controllers** with all logic inline (move to service)
- **Direct DB access from controllers** (move to repository)
- **Mixing sync/async patterns** (`.then()` and `await` mixed)
- **No validation, trusting `req.body`** (always validate at the boundary)
- **`try/catch` everywhere with the same handling** (use a central error handler)
- **Commented-out routes** (delete them)
- **Routes file with 50+ routes** (split by feature)
- **Long-running synchronous loops** that block the event loop (move to worker thread or job queue)
- **`res.send` after `res.json`** (or vice versa — sending response twice throws)
