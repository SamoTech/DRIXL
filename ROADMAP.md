# DRIXL Roadmap

## v0.1.1 - Bug Fixes & API Completeness (Current)
- [x] Message.parse() strict parameter for lenient parsing
- [x] TTL support in memory backend (parity with Redis)
- [x] Message.reply() helper for agent responses
- [x] Message.error() helper for structured ERR messages
- [x] Message.from_dict() / to_dict() for round-trip serialization
- [x] New verbs: RETRY, MERGE, SPLIT, AUTH, LOG, WAIT, CACHE
- [x] Comprehensive test coverage for new features

## v0.1.0 - Foundation (Released)
- [x] Core message builder and parser
- [x] Standard verb vocabulary (15 verbs)
- [x] In-memory context store
- [x] Custom exceptions
- [x] Basic examples
- [x] Unit tests
- [x] PyPI release
- [x] GitHub Actions CI
- [x] Auto-publish workflow

## v0.2.0 - CLI & Developer Experience
- [ ] CLI tool: `drixl parse`, `drixl build`, `drixl verbs`
- [ ] Message.estimate_tokens() for benchmarking
- [ ] Custom verb registration API
- [ ] Envelope field order independence (full fix)
- [ ] Param class with key-value structure
- [ ] Enhanced documentation site

## v0.3.0 - Async & Storage
- [ ] AsyncContextStore for async agent frameworks
- [ ] SQLite context store backend
- [ ] DynamoDB context store backend
- [ ] Message validation schema
- [ ] Context store namespaces

## v0.4.0 - Framework Adapters
- [ ] LangGraph node adapter
- [ ] CrewAI task adapter
- [ ] AutoGen message adapter
- [ ] FastAPI middleware for HTTP-based agent comms

## v0.5.0 - Observability & Security
- [ ] Message signing (HMAC)
- [ ] OpenTelemetry tracing
- [ ] Token usage tracker per pipeline
- [ ] Cost calculator (OpenAI / Anthropic pricing)
- [ ] Dashboard-ready JSON stats output

## v0.6.0 - Message Broker Integration
- [ ] Redis Streams adapter
- [ ] Kafka adapter
- [ ] RabbitMQ adapter
- [ ] NATS adapter

## v1.0.0 - Stable Release
- [ ] Full documentation site
- [ ] DRIXL Playground (web app)
- [ ] PyPI stable release
- [ ] Docker image
- [ ] Community verb extensions registry
- [ ] Benchmark CI gate
