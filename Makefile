.PHONY: dev test seed migrate api-test web-test install

dev:
	$(MAKE) -C api dev

test: api-test web-test

api-test:
	cd api && python3 -m pytest tests -q

web-test:
	cd web && pnpm test

seed:
	cd api && python3 scripts/seed_data.py

migrate:
	$(MAKE) -C api migrate

install:
	cd api && python3 -m pip install -r requirements.txt
	cd web && corepack pnpm install --frozen-lockfile
