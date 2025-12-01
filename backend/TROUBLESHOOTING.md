# Common Issues and Solutions

## MLflow Issues

### Error: AttributeError: 'EntryPoints' object has no attribute 'get'

**Problem**: MLflow 2.9.2 is incompatible with newer Python packages

**Quick Fix**:
```bash
cd backend
fix_mlflow.bat
```

**Manual Fix**:
```bash
pip install --upgrade mlflow==2.15.1
```

**Alternative**: Train without MLflow (fastest):
```bash
python train_model.py --no-mlflow
```

---

## Training Issues

### Error: Connection retries to MLflow server

**Problem**: MLflow server not running, script waiting for connection

**Solution 1 (Fastest)**: Use `--no-mlflow` flag
```bash
python train_model.py --no-mlflow
```

**Solution 2**: Start MLflow server first
```bash
# Terminal 1
start_mlflow.bat

# Terminal 2 (after server is running)
python train_model.py
```

---

## Simulator Issues

### Error: ModuleNotFoundError: No module named 'config.settings'

**Problem**: Running from wrong directory or Python path issues

**Solution**: Use the provided batch files
```bash
cd backend
run_simulator.bat
```

**Manual Fix**: Always run from backend directory
```bash
cd backend
cd simulators
python telemetry_simulator.py
```

---

## Database Issues

### Error: Connection refused to Railway PostgreSQL/Redis

**Problem**: Wrong credentials or network issue

**Solution**: Check `.env` file
```bash
# Verify these exist:
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
```

**Test Connection**:
```bash
python test_connections.py
```

---

## Agent Issues

### Error: Ray won't start

**Problem**: Existing Ray processes or port conflicts

**Solution**:
```bash
ray stop
# Then retry
python -m agents
```

### Error: No module named 'ray'

**Problem**: Ray not installed

**Solution**:
```bash
pip install ray[serve]==2.52.1
```

---

## Import Issues

### Error: Import "package" could not be resolved

**Problem**: IDE import resolution (not a runtime error)

**Why**: VS Code can't find packages in venv

**Solution**: These are warnings, not errors. Code will run fine.

**To Fix IDE**: 
1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose your venv interpreter

---

## Quick Reference

| Issue | Quick Fix Command |
|-------|------------------|
| MLflow compatibility | `fix_mlflow.bat` |
| Train without MLflow | `train_ml_model.bat` |
| Train with MLflow | `train_ml_model_with_mlflow.bat` |
| Start MLflow server | `start_mlflow.bat` |
| Start simulator | `run_simulator.bat` |
| Start ingestion | `run_ingestion.bat` |
| Start ML service | `run_ml_service.bat` |
| Start agents | `run_master_agent.bat` |
| Test connections | `python test_connections.py` |
| Test agents | `test_agents.bat` |

---

## Complete System Startup Order

1. **Optional**: Start MLflow (if you want experiment tracking)
   ```bash
   start_mlflow.bat
   ```

2. **Train Model** (first time only)
   ```bash
   train_ml_model.bat
   ```

3. **Start Services** (in separate terminals):
   ```bash
   # Terminal 1: Simulator
   run_simulator.bat
   
   # Terminal 2: Ingestion
   run_ingestion.bat
   
   # Terminal 3: ML Service
   run_ml_service.bat
   
   # Terminal 4: Master Agent
   run_master_agent.bat
   ```

4. **Verify Everything Works**
   ```bash
   # Check simulator
   curl http://localhost:8001/vehicles
   
   # Check ingestion
   curl http://localhost:8000/stats
   
   # Check ML service
   curl http://localhost:8002/model/info
   ```

---

## Performance Tips

- ✅ Use `--no-mlflow` for fastest training
- ✅ Start services in background using `start` command
- ✅ Use batch files instead of manual commands
- ✅ Close unnecessary services when not testing

---

## Getting Help

1. Check this file for your specific error
2. Review `README.md` for architecture overview
3. Check `ML_TRAINING_GUIDE.md` for training issues
4. Review `QUICKSTART_AGENTS.md` for agent issues
5. Check terminal output for specific error messages
