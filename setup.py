#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-underrated-albums.jarbasai=skill_underrated_albums:UnderratedAlbumsSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-underrated-albums',
    version='0.0.1',
    description='ovos underrated albums skill plugin',
    url='https://github.com/JarbasSkills/skill-underrated-albums',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_underrated_albums": ""},
    package_data={'skill_underrated_albums': ['locale/*', 'ui/*', 'res/*']},
    packages=['skill_underrated_albums'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
