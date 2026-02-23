# Versioning System
O projeto **SkyLab Global Market** adota o **Semantic Versioning (SemVer)** para controle de versões:

## Version Format
- **MAJOR.MINOR.PATCH**
  - MAJOR: Alterações incompatíveis com versões anteriores
  - MINOR: Adição de novas funcionalidades mantendo compatibilidade
  - PATCH: Correções de bugs ou melhorias não significativas

## Versioning Rules
1. **MAJOR Version (X.0.0)**
   - Mudanças que quebram a compatibilidade com versões anteriores
   - Grandes refatorações de código
   - Mudanças significativas na API
   - Exemplo: 2.0.0

2. **MINOR Version (0.X.0)**
   - Novas funcionalidades mantendo compatibilidade
   - Melhorias em funcionalidades existentes
   - Novos endpoints na API
   - Exemplo: 1.1.0

3. **PATCH Version (0.0.X)**
   - Correções de bugs
   - Melhorias de performance
   - Atualizações de segurança
   - Exemplo: 1.0.1

## Pre-release Versions
- Versões alfa: 1.0.0-alpha.1
- Versões beta: 1.0.0-beta.1
- Versões release candidate: 1.0.0-rc.1

## Build Metadata
- Versões com metadados de build: 1.0.0+20240321

## Versioning Examples
- 1.0.0: Primeira versão estável
- 1.0.1: Correção de bug na versão 1.0.0
- 1.1.0: Nova funcionalidade mantendo compatibilidade
- 2.0.0: Mudança que quebra compatibilidade
- 2.0.0-beta.1: Versão beta da 2.0.0
- 2.0.0+20240321: Versão 2.0.0 com metadados de build

## Versioning Process
1. Desenvolvedores criam branches para novas features
2. Pull requests são revisados e aprovados
3. Versão é incrementada conforme as mudanças
4. Tag é criada no repositório
5. Release notes são gerados
6. Deploy é realizado

## Tools
- Git para controle de versão
- GitHub/GitLab para gerenciamento de releases
- Conventional Commits para mensagens de commit
- Semantic Release para automação 